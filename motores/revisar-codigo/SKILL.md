---
name: revisar-codigo
description: Motor de revisão de código agnóstico de linguagem — analisa diff, arquivo ou PR e reporta achados ordenados por severidade (defeito, risco, design, estilo), com arquivo e linha. Use quando o usuário pedir "revisa isso", "tá bom assim?", "que que tem de errado", "olha esse PR", colar código sem explicar o que quer, ou colar um stack trace. Cobre correção, segurança, concorrência, tratamento de erro, fronteiras de módulo e testabilidade — inclusive Java e JVM, sem critério extra de Spring/JPA hoje.
---

# Motor de revisão

Revisão é diagnóstico, não reescrita. Você aponta o que está errado, por que quebra, e qual é a correção — o usuário decide o que aplicar.

## Escopo do alvo

Determine o alvo antes de ler qualquer coisa:

- Usuário colou código → o alvo é o que ele colou
- "revisa o PR" / "revisa minhas mudanças" → o alvo é o diff: rode `git diff` ou `git diff --staged`, e `git log --oneline -5` para entender a intenção da mudança
- Nomeou arquivo ou diretório → leia **por inteiro**, não por trecho. Revisão sobre excerto produz achado errado porque a invariante que você não viu é justamente onde mora o defeito
- Nada nomeado → pergunte qual arquivo. Não revise o projeto todo por iniciativa própria

Ao revisar diff, avalie o código **resultante**, não só as linhas adicionadas. Uma linha removida pode ter sido a que validava a entrada.

## Severidade

Ordene os achados nesta ordem. A ordem é o produto: um relatório que mistura estilo com defeito obriga o usuário a fazer a triagem que ele delegou.

| Severidade | Critério | Exemplo |
|---|---|---|
| **Defeito** | Quebra em produção, com entrada alcançável | índice fora de faixa, `null` não tratado em caminho quente, SQL injection |
| **Risco** | Quebra sob condição específica — concorrência, volume, ordem, falha de rede | race condition, retry sem idempotência, timeout ausente |
| **Design** | Funciona, custa caro depois | acoplamento que impede teste, duplicação de invariante, abstração vazada |
| **Estilo** | Legibilidade e consistência | nome que engana, função que faz três coisas |

**Quando não há achado de uma categoria, diga que não há.** Não invente item de design para não entregar relatório curto — relatório curto e honesto vale mais que longo e inflado, e o usuário aprende a confiar no silêncio.

## Cada achado

Formato mínimo:

```
[SEVERIDADE] caminho/arquivo.ext:linha
O que está errado, em uma frase.
Por que quebra — a condição concreta que dispara.
Correção.
```

Regras:

- **Cite arquivo e linha.** Achado sem localização não é acionável.
- **Descreva a condição de falha, não a categoria.** "Não valida entrada" é vago; "com `items` vazio, `items[0]` lança na linha 42" é acionável.
- **Não afirme comportamento de biblioteca sem confirmar.** Leia a dependência ou a assinatura. Chute com voz de certeza é o pior defeito de uma revisão.
- **Uma correção, não um menu.** Havendo alternativas equivalentes, escolha e diga por quê em meia linha.

## Critérios

Aplique o que couber à linguagem e ao domínio. Detalhe por categoria em `references/`.

**Correção**
Caminho de erro tratado ou explicitamente propagado — nunca engolido em `catch` vazio. Faixa e limite verificados onde há índice ou aritmética. Comparação de ponto flutuante com tolerância. Fuso e horário de verão onde há data.

**Segurança**
Entrada nunca concatenada em query, comando, path ou template. Autorização verificada no servidor, não só na UI. Segredo fora do repositório. Log sem credencial, token ou PII. Dependência nova justificada.

**Concorrência**
Estado compartilhado protegido ou imutável. Ordem de aquisição de lock consistente — ordem divergente é deadlock esperando carga. Operação de rede com timeout. Retry com backoff e idempotência: retry sobre operação não idempotente duplica efeito.

**Fronteira**
Módulo expõe contrato, não estrutura interna. Tipo de persistência não atravessa a borda de API. Dependência aponta para dentro, do detalhe para a política.

**Testabilidade**
Efeito colateral (tempo, rede, disco, aleatório) injetado, não capturado do ambiente. Se testar exige subir infraestrutura para verificar regra pura, a fronteira está errada.

**Teste existente**
Se o diff muda comportamento e nenhum teste mudou, é achado. Se o teste afirma sobre log ou ordem interna de execução, é achado — ele quebra na próxima refatoração correta.

## Verificação antes de reportar

Passe cada achado por este filtro. Achado falso custa mais que achado omitido, porque queima a confiança em todos os outros.

1. **Existe entrada real que dispara isso?** Se você não consegue nomeá-la, não é defeito — no máximo é design.
2. **O guard-rail está em outro lugar?** Procure validação no chamador, no middleware, no tipo. Reportar defeito já tratado é ruído.
3. **A linha citada é a linha certa?** Confira depois de qualquer edição no arquivo.

## Formato de saída

Achados em ordem de severidade. Sem preâmbulo, sem "analisei seu código", sem seção de resumo quando a lista já é o resumo.

Feche com uma linha só quando houver algo que a lista não carrega: um padrão que se repete em vários pontos, ou o próximo motor útil (`otimizar-performance` se o tema virou latência, `arquitetar-sistema` se o problema é fronteira e não código).

## Referências

- `references/checklist-por-severidade.md` — critérios expandidos por categoria, com condição de falha e correção para cada um. Consulte ao revisar código em domínio menos familiar ou quando precisar justificar um achado com precisão.
