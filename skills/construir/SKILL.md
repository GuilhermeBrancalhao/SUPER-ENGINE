---
name: construir
description: Ativa o ENGINE para começar um projeto novo do zero. Use "/construir" seguido do objetivo — é a porta de entrada amigável para quem está começando; funciona exatamente como "/engine <pedido>".
---

# /construir — porta de entrada do ENGINE

`/construir "<objetivo>"` **é** `/engine "<objetivo>"`. Não é um modo separado, é
o mesmo verbo com um nome mais convidativo para quem está abrindo o primeiro
projeto — trate o pedido como se o usuário tivesse digitado `/engine`.

```
/construir "Criar API REST de pedidos em Node.js"
/construir "App de todo list em React"
/construir "Revisar e otimizar autenticação OAuth2"
```

Siga **`skills/engine/SKILL.md`** para tudo: os verbos, o grafo de fases (que
inclui `EVOLUCAO` quando o projeto já existe), as duas portas (descoberta e
plano), a entrevista de `descoberta`, o modo `programa` para sistemas inteiros,
e os cinco invariantes. Aquele arquivo é a fonte única — este existe só para dar
um segundo nome de gatilho ao mesmo fluxo, e por isso não repete o conteúdo:
conteúdo duplicado em dois arquivos diverge assim que um deles muda e o outro
não, que foi exatamente o defeito que existia aqui antes desta revisão (a versão
anterior descrevia 8 fases sem a porta de descoberta nem o modo `programa`, e
mandava rodar `/consultar`, comando que este plugin nunca teve).

Para consultar um volume do acervo de conhecimento, leia o arquivo diretamente
em `volumes/prontos/<NN-NOME>/` — não há comando de skill para isso.
