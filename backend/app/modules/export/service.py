"""Serviço de exportação de dados — gera CSV/ZIP para backup manual do operador.

Cada função de exportação monta o CSV a partir do resultado direto da consulta
(lista de tuplas do SQLAlchemy), sem passar por uma estrutura intermediária de
dicionários — evita duplicar os dados inteiros da tabela em memória.
"""

import csv
import io
import zipfile

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.catalog import Category, Product, ProductVariant, SaleChannel, Supplier
from app.shared.models.operations import Expense, MerchandiseEntry, MerchandiseEntryItem, Sale, StockMovement

# Conjuntos de exportação disponíveis — usados tanto na validação da rota quanto no backup completo.
EXPORT_SETS = ("produtos", "vendas", "compras", "despesas", "movimentacoes", "cadastros")


def _csv_bytes(header: list[str], rows: list[list]) -> bytes:
    """Serializa cabeçalho + linhas em CSV UTF-8 com BOM (abre corretamente no Excel pt-BR)."""

    buffer = io.StringIO()
    buffer.write(chr(0xFEFF))  # BOM — escrito via chr() para evitar depender de caractere invisível no arquivo-fonte.
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _sim_nao(value: bool | None) -> str:
    """Converte booleano em Sim/Não para leitura humana no CSV."""

    return "Sim" if value else "Nao"


class ExportService:
    """Gera CSVs de backup por conjunto de dados a partir do banco de produção."""

    @staticmethod
    async def export_produtos(db: AsyncSession) -> bytes:
        """Um CSV por variante de produto — inclui estoque, preços e cadastro associado."""

        query = (
            select(
                Product.sku, Product.name, Category.name, Supplier.name,
                Product.brand, ProductVariant.size, ProductVariant.color,
                ProductVariant.stock_quantity, Product.cost_price, Product.sale_price, Product.is_active,
            )
            .join(ProductVariant, ProductVariant.product_id == Product.id)
            .outerjoin(Category, Category.id == Product.category_id)
            .outerjoin(Supplier, Supplier.id == Product.supplier_id)
            .order_by(Product.sku, ProductVariant.size, ProductVariant.color)
        )
        result = await db.execute(query)
        header = ["SKU", "Produto", "Categoria", "Fornecedor", "Marca", "Tamanho", "Cor", "Estoque", "Preco Custo", "Preco Venda", "Ativo"]
        rows = [list(r[:-1]) + [_sim_nao(r[-1])] for r in result.all()]
        return _csv_bytes(header, rows)

    @staticmethod
    async def export_vendas(db: AsyncSession) -> bytes:
        """Um CSV por venda registrada (não por item) — data, canal e total."""

        query = (
            select(Sale.sold_at, SaleChannel.name, Sale.total, Sale.notes)
            .outerjoin(SaleChannel, SaleChannel.id == Sale.sale_channel_id)
            .order_by(Sale.sold_at)
        )
        result = await db.execute(query)
        header = ["Data", "Canal", "Total", "Observacoes"]
        rows = [list(r) for r in result.all()]
        return _csv_bytes(header, rows)

    @staticmethod
    async def export_compras(db: AsyncSession) -> bytes:
        """Um CSV por entrada de mercadoria — total calculado a partir dos itens."""

        total_expr = func.coalesce(func.sum(MerchandiseEntryItem.quantity * MerchandiseEntryItem.unit_cost), 0)
        query = (
            select(MerchandiseEntry.entry_date, Supplier.name, MerchandiseEntry.notes, total_expr)
            .outerjoin(Supplier, Supplier.id == MerchandiseEntry.supplier_id)
            .outerjoin(MerchandiseEntryItem, MerchandiseEntryItem.entry_id == MerchandiseEntry.id)
            .group_by(MerchandiseEntry.id, Supplier.name)
            .order_by(MerchandiseEntry.entry_date)
        )
        result = await db.execute(query)
        header = ["Data", "Fornecedor", "Observacoes", "Total"]
        rows = [list(r) for r in result.all()]
        return _csv_bytes(header, rows)

    @staticmethod
    async def export_despesas(db: AsyncSession) -> bytes:
        """Um CSV por despesa registrada."""

        query = (
            select(Expense.date, Expense.category, Expense.amount, Expense.description, Supplier.name)
            .outerjoin(Supplier, Supplier.id == Expense.supplier_id)
            .order_by(Expense.date)
        )
        result = await db.execute(query)
        header = ["Data", "Categoria", "Valor", "Descricao", "Fornecedor"]
        rows = [list(r) for r in result.all()]
        return _csv_bytes(header, rows)

    @staticmethod
    async def export_movimentacoes(db: AsyncSession) -> bytes:
        """Um CSV por movimentação de estoque (entrada ou saída)."""

        query = (
            select(
                StockMovement.created_at, Product.sku, Product.name,
                ProductVariant.size, ProductVariant.color,
                StockMovement.movement_type, StockMovement.quantity, StockMovement.unit_cost, StockMovement.notes,
            )
            .join(ProductVariant, ProductVariant.id == StockMovement.variant_id)
            .join(Product, Product.id == ProductVariant.product_id)
            .order_by(StockMovement.created_at)
        )
        result = await db.execute(query)
        header = ["Data", "SKU", "Produto", "Tamanho", "Cor", "Tipo", "Quantidade", "Custo Unitario", "Observacoes"]
        rows = [list(r) for r in result.all()]
        return _csv_bytes(header, rows)

    @staticmethod
    async def export_cadastros(db: AsyncSession) -> bytes:
        """Um CSV combinando categorias, fornecedores e canais de venda — visão geral dos cadastros.

        Formato unificado (Tipo/Nome/Detalhes/Ativo) porque os três cadastros têm
        campos diferentes entre si; não serve para reimportação, apenas backup legível.
        """

        header = ["Tipo", "Nome", "Detalhes", "Ativo"]
        rows: list[list] = []

        cats = await db.execute(select(Category.name, Category.description))
        for name, desc in cats.all():
            rows.append(["Categoria", name, desc or "", ""])

        sups = await db.execute(select(Supplier.name, Supplier.contact, Supplier.phone, Supplier.email, Supplier.is_active))
        for name, contact, phone, email, active in sups.all():
            details = " | ".join(p for p in (
                f"Contato: {contact}" if contact else None,
                f"Telefone: {phone}" if phone else None,
                f"Email: {email}" if email else None,
            ) if p)
            rows.append(["Fornecedor", name, details, _sim_nao(active)])

        chans = await db.execute(select(SaleChannel.name, SaleChannel.fee_pct, SaleChannel.monthly_goal, SaleChannel.is_active))
        for name, fee_pct, goal, active in chans.all():
            details = f"Taxa: {fee_pct}%"
            if goal is not None:
                details += f" | Meta mensal: {goal}"
            rows.append(["Canal de venda", name, details, _sim_nao(active)])

        return _csv_bytes(header, rows)

    @staticmethod
    async def export_set(db: AsyncSession, dataset: str) -> bytes:
        """Gera o CSV de um conjunto pelo nome; levanta ValueError se o nome for inválido."""

        match dataset:
            case "produtos":
                return await ExportService.export_produtos(db)
            case "vendas":
                return await ExportService.export_vendas(db)
            case "compras":
                return await ExportService.export_compras(db)
            case "despesas":
                return await ExportService.export_despesas(db)
            case "movimentacoes":
                return await ExportService.export_movimentacoes(db)
            case "cadastros":
                return await ExportService.export_cadastros(db)
            case _:
                raise ValueError(dataset)

    @staticmethod
    async def export_backup(db: AsyncSession) -> bytes:
        """Monta um .zip com um CSV por conjunto — backup completo em um único arquivo."""

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for dataset in EXPORT_SETS:
                csv_bytes = await ExportService.export_set(db, dataset)
                zf.writestr(f"{dataset}.csv", csv_bytes)
        return buffer.getvalue()
