import { useState } from "react";
import { useNav } from "../../../app/nav";
import { AppBar, BottomNav, ScreenBody } from "../../../components/Chrome";
import { useData } from "../../../shared/hooks/useData";
import { ErrorBody, LoadingBody } from "../../../shared/ui";
import { Note } from "../../../shared/ui/Note";
import { Select } from "../../../shared/ui/Select";
import { Button } from "../../../shared/ui/Button";
import { supplierApi } from "../../auxiliaries/suppliers/api";
import { type Operation } from "../../operations/contracts";
import { api } from "../api";
import { DateFilter } from "../components/DateFilter";
import { GroupCards } from "../components/GroupCards";
import { OperationCard } from "../components/OperationCard";
import { SourceLinks } from "../components/SourceLinks";
import { type Group } from "../contracts";
import { BuyingView } from "../views/BuyingView";
import { OverviewView } from "../views/OverviewView";
import { PurchasesView } from "../views/PurchasesView";
import { ReceiptsView } from "../views/ReceiptsView";
import { SalesView } from "../views/SalesView";
import { StockView } from "../views/StockView";

const views = [
  { id: "overview", name: "Visão geral" },
  { id: "stock", name: "Estoque e giro" },
  { id: "sales", name: "Vendas e margens" },
  { id: "receipts", name: "Recebimentos" },
  { id: "purchases", name: "Compras e fornecedores" },
  { id: "buying", name: "Apoio à próxima compra" },
];
export function Management() {
  const { navigate } = useNav();
  const [view, setView] = useState("overview");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [filter, setFilter] = useState("");
  const [attribute, setAttribute] = useState("brand");
  const [sort, setSort] = useState("stock");
  const [supplier, setSupplier] = useState("");
  const scope = JSON.stringify([filter, view, supplier, sort]);
  const [paging, setPaging] = useState({ scope, offset: 0 });
  const offset = paging.scope === scope ? paging.offset : 0;
  const { data, loading, error, reload } = useData(
    () => api.report(filter, { view, offset, supplier, sort }),
    `${scope}:${offset}`,
  );
  const supplierQuery = useData(() => supplierApi.list());
  const suppliers = supplierQuery.data || [];
  const opLink = (op: Operation) => (
    <OperationCard key={op.id} operation={op} />
  );
  const sources = (ids: string[]) => <SourceLinks ids={ids} />;
  const groups = (rows: Group[]) => <GroupCards rows={rows} />;
  return (
    <>
      <AppBar title="Gestão" subtitle="Informações e suas origens" />
      <ScreenBody>
        {supplierQuery.error && (
          <ErrorBody msg={supplierQuery.error} onRetry={supplierQuery.reload} />
        )}
        <Select label="Visão" value={view} onChange={setView} options={views} />
        {view !== "stock" && (
          <DateFilter
            start={start}
            end={end}
            setStart={setStart}
            setEnd={setEnd}
            setFilter={setFilter}
          />
        )}
        {loading ? (
          <LoadingBody />
        ) : error ? (
          <ErrorBody msg={error} onRetry={reload} />
        ) : (
          data && (
            <>
              {!data.started_at && (
                <Note>
                  Confirme o inventário inicial para estabelecer o início do
                  controle.
                </Note>
              )}
              {view === "overview" && (
                <OverviewView
                  data={data}
                  setView={setView}
                  navigate={navigate}
                />
              )}
              {view === "stock" && (
                <StockView
                  data={data}
                  navigate={navigate}
                  sort={sort}
                  setSort={setSort}
                  sources={sources}
                />
              )}
              {view === "sales" && (
                <SalesView
                  data={data}
                  attribute={attribute}
                  setAttribute={setAttribute}
                  groups={groups}
                  opLink={opLink}
                />
              )}
              {view === "receipts" && (
                <ReceiptsView data={data} sources={sources} opLink={opLink} />
              )}
              {view === "purchases" && (
                <PurchasesView
                  data={data}
                  opLink={opLink}
                  supplier={supplier}
                  setSupplier={setSupplier}
                  suppliers={suppliers}
                />
              )}
              {view === "buying" && (
                <BuyingView
                  data={data}
                  sort={sort}
                  attribute={attribute}
                  setAttribute={setAttribute}
                  groups={groups}
                />
              )}
              {data.page && Object.keys(data.page.totals).length > 0 && (
                <div className="options">
                  <Button
                    disabled={offset === 0}
                    onClick={() =>
                      setPaging({ scope, offset: Math.max(0, offset - 50) })
                    }
                  >
                    Página anterior
                  </Button>
                  <span>
                    Página {Math.floor(offset / 50) + 1} · revisão{" "}
                    {data.revision}. Até 50 registros por lista. Totais
                    consideram toda a base. A base pode mudar entre páginas.
                  </span>
                  <Button
                    disabled={!data.page.has_more}
                    onClick={() => setPaging({ scope, offset: offset + 50 })}
                  >
                    Próxima página
                  </Button>
                </div>
              )}
            </>
          )
        )}
      </ScreenBody>
      <BottomNav active="intel" />
    </>
  );
}
