export const fmtBRL = (n: number) =>
  'R$ ' + Number(n).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

export const fmtBRLshort = (n: number) => {
  if (Math.abs(n) >= 1000)
    return 'R$ ' + (n / 1000).toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + 'k'
  return fmtBRL(n)
}

export const fmtNum = (n: number) => Number(n).toLocaleString('pt-BR')
