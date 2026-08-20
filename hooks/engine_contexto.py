#!/usr/bin/env python3
"""Hook UserPromptSubmit V4 — volumes dinâmicos ao vivo.

Estende V3 com detecção automática de volumes PRONTO.
Sem hardcoding de nomes - descobre dinamicamente via git.

É este hook — e não o texto de nenhuma skill — que faz o modo do motor
sobreviver à compactação do contexto: o estado em disco (`ferramentas.estado`)
não esquece, e este hook o traz de volta para dentro do turno a cada prompt.

Duas garantias de segurança valem para TODO o cartão (auditoria adversarial):

1. O teto de linhas (`teto_cartao_linhas`) só é lido via `_teto_bruto` /
   `_teto_efetivo` — nunca `int(cfg.get(...))` direto. Valor não numérico cai
   no default em vez de derrubar o cartão; teto zero/negativo é erro de
   configuração e cai no default (em `_com_avisos`) ou no piso (no cartão).
2. Todo texto que vem do estado ou de arquivo do projeto passa por `_campo`,
   que redige credenciais com `trilha.redigir` ANTES de cortar. O cartão volta
   ao contexto do modelo a cada turno — vazar `sk-…`/`ghp_…`/`AKIA…` aqui é
   pior que na trilha, que só é lida sob demanda.

DUAS RAÍZES, E ELAS NÃO SÃO A MESMA
-----------------------------------
Este hook trabalha com duas árvores diferentes, e confundi-las já custou as duas
seções mais caras do cartão:

- a raiz do **projeto hospedeiro** (`raiz_do_ciclo(cwd)`) — onde mora
  `.engine/estado.json`, e só isso;
- a raiz do **plugin** (`config.raiz_plugin()`) — onde moram `motores/*/SKILL.md`
  e `volumes/prontos/`, que viajam DENTRO do plugin.

O plugin instalado é uma cópia isolada em `~/.claude/plugins/…`; o projeto
hospedeiro é outra pasta, de outra pessoa, que obviamente não tem `motores/` nem
`volumes/prontos/`. Procurar as duas árvores na raiz do projeto fazia a seção de
volumes SUMIR por completo e as descrições de motor virarem linha pelada em todo
projeto que não fosse o próprio repositório do ENGINE — isto é, funcionava na
máquina de quem escreveu e em lugar nenhum além dela. Era o `sincronizar.py`
inteiro (42 volumes empacotados no plugin de propósito) entregue e nunca lido.

Por isso os parâmetros aqui se chamam `raiz_plugin` e `cwd`, nunca `raiz`: o nome
ambíguo é o que permitiu passar um pelo outro sem ninguém notar.
`ferramentas/cli.py` sempre fez a distinção certa
(`detectar.cartoes_do_projeto(raiz, config.raiz_plugin())`) — era este arquivo o
que estava fora do padrão.

Falha segura na direção oposta à do PreToolUse: qualquer erro devolve 0 sem
imprimir nada — o cartão é conveniência, não pode atrapalhar o turno.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import forcar_utf8, raiz_do_ciclo  # noqa: E402

forcar_utf8()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ferramentas import config, estado, trilha  # noqa: E402

# Importar módulos
try:
    from engine_analisa_diff import AnalisadorDiff
except ImportError:
    AnalisadorDiff = None

try:
    from volume_detector import DetectorVolumesAoVivo
except ImportError:
    DetectorVolumesAoVivo = None


# Mapeamento: fase → motores consultáveis
MOTORES_POR_FASE = {
    "DESCOBERTA": [],
    "ANALISE": [],
    "PLANO": ["arquitetar-sistema", "materializar-ideia"],
    "EVOLUCAO": ["arquitetar-sistema"],
    "BUILD": ["materializar-ideia", "revisar-codigo"],
    "TESTE": [],
    "REVISAO": ["revisar-codigo", "otimizar-performance", "gauntlet-loop"],
    "DOC": ["diagramar", "gauntlet-loop"],
    "ENTREGA": [],
}

INVARIANTES = (
    "1. Nunca afirmar sucesso sem ter olhado. Rodou, cola a saída; não rodou, diz que não rodou.",
    "2. Nunca ajustar o teste para o código passar. O teste é o contrato.",
    "3. Nunca inventar arquivo, API, número ou regra de negócio. Sem evidência, é pendência.",
    "4. Nunca tocar em item fora do escopo declarado do ciclo.",
    "5. Toda decisão técnica sai com a justificativa junto.",
)

# Piso do teto de linhas do cartão: as 3 linhas de cabeçalho (título, fase/modo,
# objetivo) mais as 6 do rodapé (título "Invariantes:" + os 5 invariantes). Um
# teto configurado abaixo disso é erro de configuração, não instrução — por isso
# vira piso, não é obedecido ao pé da letra.
MINIMO_CARTAO = 9

#: Default do teto quando a configuração não traz um valor utilizável.
_TETO_DEFAULT = 40


def _teto_bruto(cfg: dict) -> int:
    """Lê `cfg['teto_cartao_linhas']` e normaliza pra inteiro com segurança.

    Valor não numérico (ex.: `"abc"`) cai no default — NUNCA deixa o
    `ValueError`/`TypeError` subir, porque no hook isso viraria "cartão inteiro
    some por um erro de digitação na configuração". Todo leitor do teto neste
    arquivo passa por aqui; ninguém faz `int(cfg.get(...))` direto.
    """
    bruto = cfg.get("teto_cartao_linhas", _TETO_DEFAULT)
    try:
        return int(bruto)
    except (TypeError, ValueError):
        return _TETO_DEFAULT


def _teto_efetivo(cfg: dict) -> int:
    """Teto normalizado (`_teto_bruto`) com o piso `MINIMO_CARTAO` aplicado.

    Sem isso, `linhas[:teto]` com `teto` negativo vira "remova as últimas N
    linhas" em vez de "limite a N" — e um teto positivo mas menor que o piso
    corta cabeçalho e/ou rodapé, que são inegociáveis.
    """
    return max(_teto_bruto(cfg), MINIMO_CARTAO)


def _cortar(texto: str, limite: int) -> str:
    """Colapsa espaços e corta com reticência — protege o teto de linhas de um
    único campo gigante (ex.: objetivo de 400 caracteres) virando várias linhas."""
    texto = " ".join(str(texto).split())
    return texto if len(texto) <= limite else texto[: limite - 1] + "…"


def _campo(texto, limite: int) -> str:
    """Redige credenciais e corta no limite — todo texto vindo do estado passa aqui.

    A redação é `trilha.redigir`, de propósito por referência e não por cópia: a
    trilha é a fonte única do que conta como credencial, e duas listas de padrões
    em dois arquivos divergem na primeira vez que uma delas ganha um padrão novo.
    O cartão precisa da MESMA proteção da trilha — pior, até: a trilha é lida sob
    demanda, o cartão volta ao contexto do modelo a cada turno.

    Redigir ANTES de cortar: um token truncado pelo corte ainda seria
    reconhecível; redigido primeiro, o que sobra é só a marca.

    Vale também para texto lido de ARQUIVO do projeto (descrição de motor,
    resumo de volume): arquivo não é mais confiável que o estado.
    """
    return _cortar(trilha.redigir(str(texto)), limite)


def _ler_descricao_motor(raiz_plugin: Path, motor: str) -> Optional[str]:
    """Lê a descrição do motor de seu `SKILL.md`, na árvore do PLUGIN.

    `motores/` viaja dentro do plugin — procurar em `<projeto>/motores/` só
    acertava quando o projeto hospedeiro era o próprio repositório do ENGINE.
    """
    skill_path = raiz_plugin / "motores" / motor / "SKILL.md"
    if not skill_path.exists():
        return None

    try:
        conteudo = skill_path.read_text(encoding="utf-8")
        linhas = conteudo.split("\n")
        in_frontmatter = False
        for linha in linhas:
            if linha.startswith("---"):
                in_frontmatter = not in_frontmatter
            elif in_frontmatter and linha.startswith("description:"):
                desc = linha.replace("description:", "").strip().strip('"').strip("'")
                # Texto vindo de arquivo entra no cartão: mesma redação do estado.
                return _campo(desc, 100)
    except Exception:
        pass

    return None


def _detectar_volumes_dinamicos(raiz_plugin: Path) -> list[tuple[str, str]]:
    """Detecta volumes PRONTO em `<plugin>/volumes/prontos/`.

    A árvore é a do PLUGIN, não a do projeto hospedeiro: `volumes/prontos/` é o
    artefato que `ferramentas/sincronizar.py` gera para o plugin CARREGAR consigo
    (ver o docstring daquele módulo). Um projeto hospedeiro nunca tem essa pasta.
    """
    if not DetectorVolumesAoVivo:
        return []

    try:
        detector = DetectorVolumesAoVivo(cache_ttl_segundos=300)
        return detector.detectar_volumes(raiz_plugin)
    except Exception:
        return []


def _extrair_diff_local(cwd: str) -> str:
    """Extrai diff local via 'git diff'."""
    try:
        result = subprocess.run(
            ["git", "diff"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""


def _analisar_e_sugerir_motor(cwd: str, fase: str) -> Optional[str]:
    """Analisa diff local e sugere motor apropriado."""
    if not AnalisadorDiff:
        return None

    if fase in ["DESCOBERTA", "ANALISE"]:
        return None

    diff = _extrair_diff_local(cwd)
    if not diff or not diff.strip():
        return None

    try:
        analisador = AnalisadorDiff()
        motor = analisador.analisar_diff(diff)
        if motor:
            return analisador.gerar_sugestao(motor)
    except Exception:
        pass

    return None


def montar_cartao(dados: dict, cfg: dict) -> str:
    """Monta o cartão de estado BASE (sem as seções dinâmicas do V4), sempre
    dentro do teto efetivo de linhas.

    Mantido ao lado de `montar_cartao_estendido` para quem não tem `raiz`/`cwd`
    em mãos e para os testes de contrato de segurança: aqui não há subprocess
    nem leitura de arquivo, então o resultado é determinístico.

    O teto de `cfg['teto_cartao_linhas']` passa por `_teto_efetivo`: normalizado
    pra inteiro (valor não numérico cai no default 40) e nunca abaixo do piso
    `MINIMO_CARTAO`. Com o piso garantido, cabeçalho (fase/modo/objetivo) e
    rodapé (invariantes) NUNCA são cortados — são inegociáveis. Quem cede quando
    o orçamento de linhas aperta é o corpo (cartões, decisões, diffs pendentes,
    pendências), que pode ficar vazio.
    """
    teto = _teto_efetivo(cfg)
    ciclo = dados.get("ciclo", {})
    cabecalho = [
        "== ENGINE ativo ==",
        f"Fase: {dados.get('fase', '?')}   Modo: {ciclo.get('modo', 'normal')}",
        f"Objetivo: {_campo(ciclo.get('objetivo', ''), 160)}",
    ]
    rodape = ["Invariantes:", *INVARIANTES]

    orcamento = max(teto - len(cabecalho) - len(rodape), 0)
    corpo: list[str] = []

    def acrescentar(linha: str) -> None:
        if len(corpo) < orcamento:
            corpo.append(linha)

    cartoes = dados.get("cartoes") or []
    if cartoes:
        acrescentar(f"Cartões: {_campo(', '.join(map(str, cartoes)), 120)}")

    decisoes = dados.get("decisoes") or []
    if decisoes:
        acrescentar("Decisões:")
        for item in decisoes:
            acrescentar(
                f"  - {_campo(item.get('o_que', ''), 70)}: {_campo(item.get('porque', ''), 70)}"
            )

    diffs = dados.get("diffs_pendentes") or []
    if diffs:
        acrescentar(
            f"Diffs ({len(diffs)}): {_campo(', '.join(map(str, diffs)), 120)}"
        )

    pendencias = dados.get("pendencias") or []
    if pendencias:
        acrescentar(
            f"Pendências ({len(pendencias)}): {_campo('; '.join(map(str, pendencias)), 120)}"
        )

    linhas = cabecalho + corpo[:orcamento] + rodape
    return "\n".join(linhas[:teto])


def montar_cartao_estendido(dados: dict, cfg: dict, raiz_plugin: Path, cwd: str) -> str:
    """Monta cartão com motores + volumes dinâmicos + sugestão automática.

    `raiz_plugin` é a árvore do PLUGIN (onde estão `motores/` e
    `volumes/prontos/`); `cwd` é o diretório da sessão no projeto hospedeiro, e
    serve só para o `git diff` da sugestão automática. Ver o docstring do módulo:
    trocar um pelo outro apaga duas seções inteiras do cartão em qualquer projeto
    que não seja o repositório do próprio ENGINE.
    """
    teto = _teto_efetivo(cfg)
    ciclo = dados.get("ciclo", {})
    fase = dados.get("fase", "?")

    cabecalho = [
        "== ENGINE ativo ==",
        f"Fase: {fase}   Modo: {ciclo.get('modo', 'normal')}",
        f"Objetivo: {_campo(ciclo.get('objetivo', ''), 160)}",
    ]
    rodape = ["Invariantes:", *INVARIANTES]

    orcamento = max(teto - len(cabecalho) - len(rodape), 0)
    corpo: list[str] = []

    def acrescentar(linha: str) -> None:
        if len(corpo) < orcamento:
            corpo.append(linha)

    # Seção: Motores da fase
    motores = MOTORES_POR_FASE.get(fase, [])
    if motores:
        acrescentar("📋 Motores desta fase:")
        for motor in motores:
            desc = _ler_descricao_motor(raiz_plugin, motor)
            if desc:
                acrescentar(f"  • {motor}: {desc}")
            else:
                acrescentar(f"  • {motor}")

    # Seção: Sugestão automática de motor (o texto vem de constantes internas do
    # analisador — o diff só escolhe QUAL motor — então não precisa de redação)
    sugestao = _analisar_e_sugerir_motor(str(cwd), fase)
    if sugestao:
        acrescentar(sugestao)

    # Seção: Volumes PRONTO (detectados na árvore do PLUGIN, não na do projeto)
    volumes_dinamicos = _detectar_volumes_dinamicos(raiz_plugin)

    if volumes_dinamicos:
        acrescentar("📚 Volumes PRONTO (consultáveis):")
        for vol_nome, vol_resumo in volumes_dinamicos:
            # Nome e resumo vêm de arquivo do projeto: mesma redação do estado.
            acrescentar(f"  • {_campo(vol_nome, 60)}: {_campo(vol_resumo, 100)}")

    # Seção: Cartões (original)
    cartoes = dados.get("cartoes") or []
    if cartoes:
        acrescentar(f"Cartões: {_campo(', '.join(map(str, cartoes)), 120)}")

    # Seção: Decisões (original)
    decisoes = dados.get("decisoes") or []
    if decisoes:
        acrescentar("Decisões:")
        for item in decisoes:
            acrescentar(f"  - {_campo(item.get('o_que', ''), 60)}")

    # Seção: Diffs pendentes (original)
    diffs = dados.get("diffs_pendentes") or []
    if diffs:
        acrescentar(f"Diffs ({len(diffs)}): {_campo(', '.join(map(str, diffs)), 100)}")

    # Seção: Pendências (original — segue no cartão: pendência fora do cartão é
    # pendência esquecida)
    pendencias = dados.get("pendencias") or []
    if pendencias:
        acrescentar(
            f"Pendências ({len(pendencias)}): {_campo('; '.join(map(str, pendencias)), 120)}"
        )

    linhas = cabecalho + corpo[:orcamento] + rodape
    return "\n".join(linhas[:teto])


#: Quantas linhas o cabeçalho ocupa (título, fase/modo, objetivo). O rodapé tem
#: `1 + len(INVARIANTES)`. Os dois são inegociáveis; quem cede espaço é o corpo.
_LINHAS_CABECALHO = 3


def _partir_cartao(linhas: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Separa o cartão em (cabeçalho, corpo, rodapé).

    O rodapé é reconhecido pela sua forma exata (`"Invariantes:"` seguido dos
    invariantes) no fim da lista. Se não estiver lá — cartão truncado por um teto
    apertadíssimo —, não há rodapé a preservar e tudo vira corpo.
    """
    tamanho_rodape = 1 + len(INVARIANTES)
    corte = len(linhas) - tamanho_rodape
    if corte >= _LINHAS_CABECALHO and linhas[corte] == "Invariantes:":
        return linhas[:_LINHAS_CABECALHO], linhas[_LINHAS_CABECALHO:corte], linhas[corte:]
    return linhas[:_LINHAS_CABECALHO], linhas[_LINHAS_CABECALHO:], []


def _com_avisos(cartao: str, cfg: dict) -> str:
    """Acrescenta os avisos de configuração (`cfg['_avisos']`) ao cartão, sem nunca
    furar o teto de linhas — os avisos entram no mesmo orçamento, não por fora dele.

    Eles entram ANTES do rodapé, tomando o espaço do CORPO. Empilhá-los no fim e
    cortar em `linhas[:teto]` era o mesmo que não emiti-los: assim que o cartão
    passou a trazer as seções de motores e volumes (que só apareciam no
    repositório do próprio ENGINE — ver o docstring do módulo), ele já chegava
    aqui no teto, e todo aviso caía no corte. Aviso de configuração que nunca é
    exibido é configuração quebrada invisível, que é exatamente o que ele existe
    para impedir.

    O teto passa por `_teto_bruto` (nunca por `int(cfg.get(...))` direto): um valor
    não numérico aqui derrubava o cartão inteiro — o `ValueError` subia até o
    `try/except` de `principal()`, que devolve 0 sem imprimir nada. E teto zero ou
    negativo não é "limite apertado", é erro de configuração: `linhas[:0]` apagava
    o cartão por completo e `linhas[:-n]` removia as últimas linhas — os
    invariantes do rodapé e o próprio aviso que deveria aparecer. Nesses casos o
    teto cai no default, o mesmo destino do valor não numérico. Teto positivo
    continua sendo obedecido à risca, como sempre foi.
    """
    avisos = cfg.get("_avisos") or []
    if not avisos:
        return cartao
    teto = _teto_bruto(cfg)
    if teto < 1:
        teto = _TETO_DEFAULT

    cabecalho, corpo, rodape = _partir_cartao(cartao.splitlines())
    # Aviso também é texto que veio de fora (nome de chave, item de config do
    # projeto): recebe a mesma redação do resto do cartão.
    novos = [f"ENGINE aviso: {trilha.redigir(str(aviso))}" for aviso in avisos]

    disponivel = max(teto - len(cabecalho) - len(rodape), 0)
    novos = novos[:disponivel]
    corpo = corpo[: max(disponivel - len(novos), 0)]
    return "\n".join((cabecalho + corpo + novos + rodape)[:teto])


def principal() -> int:
    # Ao contrário do PreToolUse, aqui qualquer falha no caminho (entrada
    # ilegível, estado corrompido, config quebrada, bug na montagem do cartão)
    # devolve 0 sem imprimir nada. Nunca deixa a exceção subir: o cartão é
    # conveniência, não pode atrapalhar o turno do usuário.
    try:
        try:
            evento = json.load(sys.stdin)
        except Exception:  # noqa: BLE001
            return 0

        if not isinstance(evento, dict):
            return 0

        cwd = evento.get("cwd") or "."
        # A raiz do PROJETO é usada só para achar o estado. As árvores de
        # `motores/` e `volumes/prontos/` são do PLUGIN — ver o docstring do
        # módulo. Passar `raiz` aqui embaixo é o bug que apagava as duas seções
        # em todo projeto hospedeiro.
        raiz = raiz_do_ciclo(Path(cwd))

        dados = estado.carregar(raiz)
        if not dados or not dados.get("ativo"):
            return 0

        cfg = config.carregar(raiz)
        cartao = montar_cartao_estendido(dados, cfg, config.raiz_plugin(), cwd)
        cartao = _com_avisos(cartao, cfg)

        if cartao.strip():
            print(cartao)
        return 0
    except Exception:  # noqa: BLE001
        return 0


if __name__ == "__main__":
    sys.exit(principal())
