import { Card, Section } from "../../../shared/ui";
import { Button } from "../../../shared/ui/Button";
import { Field } from "../../../shared/ui/Field";
import { Note } from "../../../shared/ui/Note";
import { Select } from "../../../shared/ui/Select";
import { useEditor } from "../hooks/EditorContext";
import { addPayment, removePayment } from "../model/payments";
export function OperationPayments() {
  const { kind, input, patch, paymentPatch, options } = useEditor();
  return (
    <>
      {kind === "sale" && (
        <Section title="Pagamentos recebidos">
          <Note>
            Sem pagamento inicial, a venda ficará pendente. Não há vencimento
            nem agenda de parcelas.
          </Note>
          {input.payments.map((payment, index) => (
            <Card key={payment.id || index}>
              <Field
                label="Valor recebido"
                type="number"
                value={payment.amount}
                onChange={(value) => paymentPatch(index, { amount: value })}
                required
              />
              <Select
                label="Forma de pagamento"
                value={payment.method_id}
                onChange={(value) => paymentPatch(index, { method_id: value })}
                options={options("payment_method", payment.method_id)}
                required
              />
              <Button
                danger
                onClick={() =>
                  patch({
                    payments: removePayment(input.payments, index),
                  })
                }
              >
                Remover pagamento
              </Button>
            </Card>
          ))}
          <Button
            onClick={() =>
              patch({
                payments: addPayment(input.payments),
              })
            }
          >
            Adicionar pagamento
          </Button>
        </Section>
      )}
    </>
  );
}
