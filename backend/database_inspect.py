"""Diagnóstico administrativo somente leitura, sem corpos de operações ou segredos."""

import argparse
import asyncio
import json
from pathlib import Path

from admin_config import migration_url
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from app.shared.models.entities import Base
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine


async def diagnose(url):
    engine = create_async_engine(url, hide_parameters=True)
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SET TRANSACTION READ ONLY"))

            def schema(sync):
                inspector = inspect(sync)
                actual = set(inspector.get_table_names(schema="public"))
                checks = {
                    table: inspector.get_check_constraints(table)
                    for table in sorted(actual)
                    if table.startswith("lgd_")
                }
                missing_checks = {
                    table.name: sorted(
                        {
                            str(c.name)
                            for c in table.constraints
                            if c.__class__.__name__ == "CheckConstraint"
                        }
                        - {c["name"] for c in checks.get(table.name, [])}
                    )
                    for table in Base.metadata.sorted_tables
                }
                return {
                    "tables": sorted(actual),
                    "drift": compare_metadata(
                        MigrationContext.configure(
                            sync, opts={"compare_type": True, "compare_server_default": True}
                        ),
                        Base.metadata,
                    ),
                    "check_definitions": checks,
                    "missing_checks": {
                        table: names for table, names in missing_checks.items() if names
                    },
                }

            report = await connection.run_sync(schema)
            report["relations"] = [
                dict(row)
                for row in (
                    await connection.execute(
                        text(
                            "SELECT relname AS table_name, n_live_tup AS estimated_live_rows, n_dead_tup AS estimated_dead_rows, last_autovacuum, last_autoanalyze, pg_total_relation_size(relid) AS total_bytes, pg_indexes_size(relid) AS index_bytes FROM pg_stat_user_tables WHERE schemaname='public' ORDER BY relname"
                        )
                    )
                ).mappings()
            ]
            report["sessions"] = [
                dict(row)
                for row in (
                    await connection.execute(
                        text(
                            "SELECT application_name, state, count(*) AS connections, max(EXTRACT(EPOCH FROM now()-xact_start)) AS oldest_transaction_seconds FROM pg_stat_activity WHERE datname=current_database() GROUP BY application_name,state ORDER BY application_name,state"
                        )
                    )
                ).mappings()
            ]
            report["settings"] = dict(
                (
                    await connection.execute(
                        text(
                            "SELECT current_database() AS database, current_user AS diagnostic_role, current_setting('server_version') AS postgres, current_setting('autovacuum') AS autovacuum, current_setting('max_connections') AS max_connections"
                        )
                    )
                )
                .mappings()
                .one()
            )
            report["permissions"] = [
                dict(row)
                for row in (
                    await connection.execute(
                        text(
                            "SELECT tablename, tableowner, has_table_privilege('lgd_app',quote_ident(tablename),'SELECT') AS can_select, has_table_privilege('lgd_app',quote_ident(tablename),'INSERT') AS can_insert, has_table_privilege('lgd_app',quote_ident(tablename),'UPDATE') AS can_update, has_table_privilege('lgd_app',quote_ident(tablename),'DELETE') AS can_delete, has_table_privilege('lgd_app',quote_ident(tablename),'TRUNCATE') AS can_truncate FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
                        )
                    )
                ).mappings()
            ]
            report["documents"] = {}
            for table, column in (
                ("lgd_operations", "result"),
                ("lgd_revisions", "after"),
                ("lgd_requests", "response"),
            ):
                report["documents"][table] = dict(
                    (
                        await connection.execute(
                            text(
                                f'SELECT count(*) AS rows, COALESCE(sum(pg_column_size("{column}")),0) AS stored_document_bytes, COALESCE(max(pg_column_size("{column}")),0) AS largest_document_bytes FROM "{table}"'
                            )
                        )
                    )
                    .mappings()
                    .one()
                )
            await connection.rollback()
            report["read_only"] = True
            return report
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = json.dumps(
        asyncio.run(diagnose(migration_url())), ensure_ascii=False, indent=2, default=str
    )
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
    else:
        print(result)
