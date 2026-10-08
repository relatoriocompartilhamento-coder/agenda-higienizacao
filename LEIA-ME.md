# Avisos das ações de higienização no Telegram

Todo dia às 10h (horário de Brasília) o GitHub confere a `agenda.csv`.
Se houver ação no dia seguinte, o bot manda uma mensagem no Telegram com
município, trecho, horário e o link do ponto de encontro.

## Arquivos
- `agenda.csv` – a agenda. Uma linha por logradouro/trecho. É o único arquivo que você edita.
- `avisar.py` – o programa que monta e envia a mensagem.
- `.github/workflows/aviso.yml` – o agendamento diário no GitHub.

## Colunas da agenda.csv (separadas por ponto e vírgula)
data (dd/mm/aaaa) ; municipio ; bairro ; acao (número) ; logradouro ; trecho ; postes ; horario ; ponto_encontro ; latitude ; longitude

Campos podem ficar vazios, exceto a data. Linhas com a mesma data e o mesmo
município/ação aparecem juntas na mesma mensagem.

## Incluir um cronograma novo ou mudar uma data
1. No GitHub, abra `agenda.csv` e clique no lápis (Edit).
2. Acrescente ou altere as linhas. Não apague a primeira linha (cabeçalho).
3. Clique em "Commit changes". Pronto, já vale para o aviso do dia seguinte.

## Testar
Aba Actions → "Aviso de ações no Telegram" → Run workflow → modo `proxima` → Run.
A próxima ação da agenda chega no Telegram em cerca de 1 minuto.

## Mudar o horário do aviso
No `aviso.yml`, a linha `cron: "0 13 * * *"` está em horário UTC (Brasília + 3h).
Ex.: 6h → `"0 9 * * *"`; 8h → `"0 11 * * *"`. O GitHub pode atrasar alguns minutos.
