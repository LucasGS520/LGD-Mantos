"""Provisiona apenas os papéis LGD e a propriedade do schema no banco indicado."""

import asyncio

import asyncpg
from admin_config import environment
from sqlalchemy.engine import make_url


async def bootstrap():
    config = environment()
    parsed = make_url(config["BOOTSTRAP_DATABASE_URL"])
    if parsed.database not in {"lgd_mantos", "lgd_mantos_alignment_test"}:
        raise RuntimeError("Bootstrap permitido somente nos bancos LGD")
    connection = await asyncpg.connect(
        parsed.set(drivername="postgresql").render_as_string(hide_password=False)
    )
    try:
        if await connection.fetchval("SELECT current_database()") != parsed.database:
            raise RuntimeError("Destino administrativo divergente")
        async with connection.transaction():
            for role, key in (
                ("lgd_app", "LGD_APP_PASSWORD"),
                ("lgd_migrator", "LGD_MIGRATOR_PASSWORD"),
            ):
                password = config.get(key)
                if not password:
                    raise RuntimeError("Defina as duas senhas de papéis LGD")
                exists = await connection.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=$1)", role
                )
                if exists and await connection.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM pg_auth_members m JOIN pg_roles parent ON parent.oid=m.roleid WHERE member=(SELECT oid FROM pg_roles WHERE rolname=$1) AND NOT ($1='lgd_migrator' AND parent.rolname='lgd_app'))",
                    role,
                ):
                    raise RuntimeError(
                        "Papéis LGD não podem herdar outros papéis; regularize a associação explicitamente"
                    )
                command = await connection.fetchval(
                    "SELECT format($1, $2::text, $3::text)",
                    ("ALTER" if exists else "CREATE")
                    + " ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD %L",
                    role,
                    password,
                )
                await connection.execute(command)
            # O administrador pode observar sessões do app, nunca o contrário.
            await connection.execute("GRANT lgd_app TO lgd_migrator")
            await connection.execute("ALTER SCHEMA public OWNER TO lgd_migrator")
            for statement in (
                "REVOKE CREATE, TEMPORARY ON DATABASE %I FROM PUBLIC",
                "GRANT CONNECT ON DATABASE %I TO lgd_app, lgd_migrator",
                "GRANT CREATE, TEMPORARY ON DATABASE %I TO lgd_migrator",
            ):
                await connection.execute(
                    await connection.fetchval(
                        "SELECT format($1, $2::text)", statement, parsed.database
                    )
                )
            await connection.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
            await connection.execute("GRANT USAGE ON SCHEMA public TO lgd_app")
        print("Papéis LGD provisionados; nenhuma tabela ou operação foi criada")
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
