#!/usr/bin/env python3
"""Testes de integração do hook VIVO `hooks/engine_contexto.py`.

Cobrem o cartão estendido de ponta a ponta: motores por fase, sugestão
automática via diff, volumes PRONTO detectados dinamicamente e o teto de
linhas. Este arquivo nasceu dos antigos testes das cópias `engine_contexto_v3`
e `engine_contexto_v4` (removidas), reapontados para o módulo que o
`hooks.json` executa de verdade.
"""
import json
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "hooks"))

# O hook vivo — o mesmo caminho de import de test_hooks.py, para que o módulo
# exista uma única vez na sessão do pytest.
import engine_contexto as hook  # noqa: E402

RAIZ_PLUGIN = Path(__file__).resolve().parent.parent.parent


def criar_estrutura_teste(tmp_path: Path, volumes=("07-PROMPT-ENGINE", "12-MEMORY", "31-TESTING", "99-NOVO-VOLUME")) -> Path:
    """Cria um PLUGIN de mentira: `motores/` e `volumes/prontos/`.

    Estas duas árvores são do plugin, não do projeto hospedeiro — é por isso que
    o valor devolvido aqui é passado como `raiz_plugin` a
    `montar_cartao_estendido`, e nunca como raiz de projeto.
    """
    for motor_nome in [
        "revisar-codigo",
        "materializar-ideia",
        "otimizar-performance",
        "arquitetar-sistema",
    ]:
        motor_dir = tmp_path / "motores" / motor_nome
        motor_dir.mkdir(parents=True)
        (motor_dir / "SKILL.md").write_text(
            f'---\nname: {motor_nome}\ndescription: "Teste {motor_nome}"\n---\n',
            encoding="utf-8",
        )

    for vol_nome in volumes:
        vol_dir = tmp_path / "volumes" / "prontos" / vol_nome
        vol_dir.mkdir(parents=True)
        (vol_dir / "README.md").write_text(
            f"# {vol_nome}\n\nDescrição dinamicamente descoberta",
            encoding="utf-8",
        )

    return tmp_path


# --- Contrato de superfície do módulo vivo ---------------------------------------


def test_hook_expoe_a_superficie_esperada():
    """O módulo vivo expõe as funções que o cartão estendido usa."""
    assert hasattr(hook, "montar_cartao_estendido")
    assert hasattr(hook, "_analisar_e_sugerir_motor")
    assert hasattr(hook, "_detectar_volumes_dinamicos")


# --- Cartão estendido: fases e teto ----------------------------------------------


def test_monta_cartao_na_fase_plano(tmp_path):
    """Cartão da fase PLANO traz cabeçalho, invariantes e os motores da fase."""
    raiz = criar_estrutura_teste(tmp_path)

    dados = {
        "ativo": True,
        "ciclo": {
            "id": "test-cycle",
            "objetivo": "Testar motor sugerido",
            "modo": "normal",
        },
        "fase": "PLANO",
        "cartoes": ["python"],
        "decisoes": [],
        "diffs_pendentes": [],
    }
    cfg = {"teto_cartao_linhas": 50}

    cartao = hook.montar_cartao_estendido(dados, cfg, raiz, str(raiz))

    assert cartao is not None
    assert "== ENGINE ativo ==" in cartao
    assert "PLANO" in cartao
    assert "Invariantes:" in cartao
    # Motores da fase PLANO, lidos do MOTORES_POR_FASE vivo
    assert "arquitetar-sistema" in cartao
    assert "materializar-ideia" in cartao
    assert len(cartao.split("\n")) <= 50


def test_gauntlet_loop_e_consultavel_em_revisao(tmp_path):
    """O motor gauntlet-loop aparece no cartão da fase REVISAO, junto dos motores
    de critério já existentes -- regra fixa em MOTORES_POR_FASE, não decisão do
    modelo em tempo de execução."""
    raiz = criar_estrutura_teste(tmp_path)

    dados = {
        "ativo": True,
        "ciclo": {"id": "test-cycle", "objetivo": "Testar gauntlet-loop", "modo": "normal"},
        "fase": "REVISAO",
        "cartoes": ["python"],
        "decisoes": [],
        "diffs_pendentes": [],
    }
    cfg = {"teto_cartao_linhas": 50}

    cartao = hook.montar_cartao_estendido(dados, cfg, raiz, str(raiz))

    assert "gauntlet-loop" in cartao
    assert "revisar-codigo" in cartao
    assert "otimizar-performance" in cartao


def test_gauntlet_loop_e_consultavel_em_doc(tmp_path):
    """O motor gauntlet-loop aparece no cartão da fase DOC, junto de diagramar."""
    raiz = criar_estrutura_teste(tmp_path)

    dados = {
        "ativo": True,
        "ciclo": {"id": "test-cycle", "objetivo": "Testar gauntlet-loop", "modo": "normal"},
        "fase": "DOC",
        "cartoes": ["python"],
        "decisoes": [],
        "diffs_pendentes": [],
    }
    cfg = {"teto_cartao_linhas": 50}

    cartao = hook.montar_cartao_estendido(dados, cfg, raiz, str(raiz))

    assert "gauntlet-loop" in cartao
    assert "diagramar" in cartao


def test_motor_gauntlet_loop_tem_skill_md_real():
    """O SKILL.md real do motor (não o de teste) existe na árvore do plugin e
    declara `name`/`description` -- é o arquivo que o hook lê em produção."""
    skill_path = RAIZ_PLUGIN / "motores" / "gauntlet-loop" / "SKILL.md"
    assert skill_path.exists()

    conteudo = skill_path.read_text(encoding="utf-8")
    assert "name: gauntlet-loop" in conteudo
    assert "description:" in conteudo


def test_respeita_teto_em_build(tmp_path):
    """Teto de 50 linhas é respeitado mesmo com corpo cheio."""
    raiz = criar_estrutura_teste(tmp_path)

    dados = {
        "ativo": True,
        "ciclo": {
            "id": "test-cycle",
            "objetivo": "Objetivo muito longo que poderia ocupar várias linhas",
            "modo": "normal",
        },
        "fase": "BUILD",
        "cartoes": ["python", "pytest", "docker"],
        "decisoes": [
            {"o_que": "Usar pattern A"},
            {"o_que": "Usar pattern B"},
        ],
        "diffs_pendentes": ["file1.py", "file2.py", "file3.py"],
    }
    cfg = {"teto_cartao_linhas": 50}

    cartao = hook.montar_cartao_estendido(dados, cfg, raiz, str(raiz))

    assert len(cartao.split("\n")) <= 50


def test_nao_sugere_motor_em_descoberta(tmp_path):
    """Em DESCOBERTA o hook nunca sugere motor (retorna antes de olhar o diff)."""
    raiz = criar_estrutura_teste(tmp_path)

    dados = {
        "ativo": True,
        "ciclo": {"objetivo": "Teste", "modo": "normal"},
        "fase": "DESCOBERTA",
        "cartoes": [],
        "decisoes": [],
        "diffs_pendentes": [],
    }
    cfg = {"teto_cartao_linhas": 50}

    cartao = hook.montar_cartao_estendido(dados, cfg, raiz, str(raiz))

    assert "💡 Sugestão" not in cartao


def test_funcoes_auxiliares():
    """_cortar respeita o limite; _teto_efetivo nunca fica abaixo do piso."""
    cortado = hook._cortar("a" * 200, 50)
    assert len(cortado) <= 50

    teto = hook._teto_efetivo({})
    assert teto >= hook.MINIMO_CARTAO


# --- Volumes dinâmicos ------------------------------------------------------------


def test_detecta_volumes_dinamicamente(tmp_path):
    """Detecção lista exatamente o que está em volumes/prontos/."""
    raiz = criar_estrutura_teste(tmp_path)

    volumes = hook._detectar_volumes_dinamicos(raiz)

    assert len(volumes) == 4
    nomes = [v[0] for v in volumes]
    assert "07-PROMPT-ENGINE" in nomes
    assert "99-NOVO-VOLUME" in nomes


def test_monta_cartao_com_volumes(tmp_path):
    """Cartão inclui a seção de volumes PRONTO com os nomes detectados."""
    raiz = criar_estrutura_teste(tmp_path)

    dados = {
        "ativo": True,
        "ciclo": {"objetivo": "Teste volumes dinâmicos", "modo": "normal"},
        "fase": "BUILD",
        "cartoes": ["python"],
        "decisoes": [],
        "diffs_pendentes": [],
    }
    cfg = {"teto_cartao_linhas": 50}

    cartao = hook.montar_cartao_estendido(dados, cfg, raiz, str(raiz))

    assert "== ENGINE ativo ==" in cartao
    assert "BUILD" in cartao
    assert "Volumes PRONTO" in cartao
    assert "07-PROMPT-ENGINE" in cartao
    assert "99-NOVO-VOLUME" in cartao
    assert len(cartao.split("\n")) <= 50


def test_volume_novo_descoberto_sem_mudar_codigo(tmp_path):
    """Volume criado depois aparece no cartão — nada de lista hardcoded."""
    raiz = criar_estrutura_teste(tmp_path)

    novo_vol = raiz / "volumes" / "prontos" / "55-NOVO-DESCOBERTO"
    novo_vol.mkdir(parents=True)
    (novo_vol / "README.md").write_text(
        "# 55-NOVO-DESCOBERTO\n\nNovo volume descoberto", encoding="utf-8"
    )

    dados = {
        "ativo": True,
        "ciclo": {"objetivo": "Teste", "modo": "normal"},
        "fase": "DOC",
        "cartoes": [],
        "decisoes": [],
        "diffs_pendentes": [],
    }
    cfg = {"teto_cartao_linhas": 50}

    cartao = hook.montar_cartao_estendido(dados, cfg, raiz, str(raiz))

    assert "55-NOVO-DESCOBERTO" in cartao


def test_volumes_em_ordem_alfabetica(tmp_path):
    """Volumes aparecem no cartão em ordem alfabética."""
    raiz = criar_estrutura_teste(tmp_path)

    dados = {
        "ativo": True,
        "ciclo": {"objetivo": "Teste", "modo": "normal"},
        "fase": "PLANO",
        "cartoes": [],
        "decisoes": [],
        "diffs_pendentes": [],
    }
    cfg = {"teto_cartao_linhas": 50}

    cartao = hook.montar_cartao_estendido(dados, cfg, raiz, str(raiz))

    linhas = cartao.split("\n")
    vol_indices = []
    for i, linha in enumerate(linhas):
        for nome in ("07-PROMPT-ENGINE", "12-MEMORY", "31-TESTING", "99-NOVO-VOLUME"):
            if nome in linha:
                vol_indices.append((i, nome))

    esperado = ["07-PROMPT-ENGINE", "12-MEMORY", "31-TESTING", "99-NOVO-VOLUME"]
    obtido = [nome for _, nome in sorted(vol_indices)]
    assert obtido == esperado, f"Esperado {esperado}, obteve {obtido}"


def test_volume_com_status_nao_pronto_fica_fora_do_cartao(tmp_path):
    """`_VOLUME.yml` com status != PRONTO exclui o volume do cartão.

    Este é o comportamento vivo que substituiu a lista hardcoded
    `VOLUMES_PRONTOS` das cópias antigas: quem manda é o `status` do
    `_VOLUME.yml`, não o código.
    """
    raiz = criar_estrutura_teste(tmp_path, volumes=("31-TESTING",))

    rascunho = raiz / "volumes" / "prontos" / "40-RASCUNHO"
    rascunho.mkdir(parents=True)
    (rascunho / "_VOLUME.yml").write_text(
        "status: RASCUNHO\nescopo: Ainda em escrita\n", encoding="utf-8"
    )
    (rascunho / "README.md").write_text("# 40-RASCUNHO\n\nEm escrita", encoding="utf-8")

    dados = {
        "ativo": True,
        "ciclo": {"objetivo": "Teste", "modo": "normal"},
        "fase": "BUILD",
        "cartoes": [],
        "decisoes": [],
        "diffs_pendentes": [],
    }
    cfg = {"teto_cartao_linhas": 50}

    cartao = hook.montar_cartao_estendido(dados, cfg, raiz, str(raiz))

    assert "31-TESTING" in cartao
    assert "40-RASCUNHO" not in cartao


def test_volume_pronto_usa_escopo_do_volume_yml_como_resumo(tmp_path):
    """Com `_VOLUME.yml` `status: PRONTO`, o resumo do cartão vem do `escopo`."""
    raiz = criar_estrutura_teste(tmp_path, volumes=())

    vol = raiz / "volumes" / "prontos" / "12-MEMORY"
    vol.mkdir(parents=True)
    (vol / "_VOLUME.yml").write_text(
        "status: PRONTO\nescopo: Persistência de estado entre sessões\n",
        encoding="utf-8",
    )

    dados = {
        "ativo": True,
        "ciclo": {"objetivo": "Teste", "modo": "normal"},
        "fase": "BUILD",
        "cartoes": [],
        "decisoes": [],
        "diffs_pendentes": [],
    }
    cfg = {"teto_cartao_linhas": 50}

    cartao = hook.montar_cartao_estendido(dados, cfg, raiz, str(raiz))

    assert "12-MEMORY" in cartao
    assert "Persistência de estado entre sessões" in cartao


# --- A trava: as duas raizes nao podem voltar a ser a mesma -----------------------


def _estado_de_teste(fase: str = "BUILD") -> dict:
    return {
        "versao": 1,
        "ativo": True,
        "ciclo": {
            "id": "2026-08-04-1",
            "objetivo": "trabalhar num projeto hospedeiro qualquer",
            "iniciado_em": "2026-08-04T10:00:00",
            "modo": "normal",
        },
        "fase": fase,
        "fases_concluidas": [],
        "cartoes": ["python"],
        "decisoes": [],
        "pendencias": [],
        "diffs_pendentes": [],
        "cobrancas_por_fase": {},
        "historico": ["2026-08-04-1"],
    }


def _rodar_hook_vivo(cwd: Path) -> str:
    """Roda `hooks/engine_contexto.py` como subprocesso, igual ao Claude Code."""
    evento = json.dumps({"cwd": str(cwd), "hook_event_name": "UserPromptSubmit"})
    resultado = subprocess.run(
        [sys.executable, str(RAIZ_PLUGIN / "hooks" / "engine_contexto.py")],
        input=evento.encode("utf-8"),
        capture_output=True,
    )
    assert resultado.returncode == 0, resultado.stderr.decode("utf-8", "replace")
    return resultado.stdout.decode("utf-8", "replace")


def _projeto_hospedeiro(tmp_path: Path, fase: str = "BUILD") -> Path:
    projeto = tmp_path / "projeto-de-outra-pessoa"
    (projeto / ".engine").mkdir(parents=True)
    (projeto / "app.py").write_text("print('oi')\n", encoding="utf-8")
    (projeto / ".engine" / "estado.json").write_text(
        json.dumps(_estado_de_teste(fase), ensure_ascii=False), encoding="utf-8"
    )
    return projeto


def test_o_projeto_hospedeiro_nao_tem_as_arvores_do_plugin(tmp_path):
    """Premissa da trava: um projeto qualquer nao tem motores/ nem volumes/prontos/.

    Se este teste falhar, os dois abaixo nao provam nada -- estariam achando as
    arvores no lugar errado por acidente.
    """
    projeto = _projeto_hospedeiro(tmp_path)

    assert not (projeto / "motores").exists()
    assert not (projeto / "volumes" / "prontos").exists()
    assert (RAIZ_PLUGIN / "motores").is_dir()
    assert (RAIZ_PLUGIN / "volumes" / "prontos").is_dir()


def test_o_cartao_traz_os_volumes_do_plugin_num_projeto_hospedeiro(tmp_path):
    """A secao de volumes vem da arvore do PLUGIN, nunca da do projeto.

    Este e o teste que reprova a regressao original: `principal()` passava a raiz
    do projeto hospedeiro a `montar_cartao_estendido`, e a secao inteira de
    volumes -- os 42 volumes que `ferramentas/sincronizar.py` empacota no plugin
    justamente para viajarem com ele -- simplesmente nao aparecia em NENHUM
    projeto que nao fosse o proprio repositorio do ENGINE.

    Nomes de volume nao sao fixados aqui de proposito: o acervo cresce. O que se
    exige e que a secao exista e que os volumes citados sejam os que estao em
    disco no plugin AGORA.
    """
    projeto = _projeto_hospedeiro(tmp_path)

    cartao = _rodar_hook_vivo(projeto)

    assert "Volumes PRONTO" in cartao, (
        "a secao de volumes sumiu do cartao -- provavelmente a raiz do projeto "
        f"voltou a ser usada no lugar da raiz do plugin. Cartao:\n{cartao}"
    )
    do_disco = {caminho.name for caminho in (RAIZ_PLUGIN / "volumes" / "prontos").iterdir() if caminho.is_dir()}
    citados = {nome for nome in do_disco if nome in cartao}
    assert citados, f"nenhum volume real citado. Em disco: {sorted(do_disco)}"


def test_o_cartao_traz_a_descricao_dos_motores_num_projeto_hospedeiro(tmp_path):
    """As descricoes vem de `<plugin>/motores/*/SKILL.md`, nao de `<projeto>/motores/`.

    Falha mais silenciosa que a dos volumes: a secao continuava aparecendo, so
    que com o nome pelado do motor e sem uma palavra sobre o que ele faz -- e
    nome de motor sozinho nao ajuda o modelo a decidir se vale consultar.
    """
    projeto = _projeto_hospedeiro(tmp_path, fase="BUILD")

    cartao = _rodar_hook_vivo(projeto)

    linhas_de_motor = [
        linha for linha in cartao.splitlines() if "materializar-ideia" in linha
    ]
    assert linhas_de_motor, f"motor da fase BUILD ausente do cartao:\n{cartao}"
    assert any(
        "materializar-ideia:" in linha for linha in linhas_de_motor
    ), (
        "o motor aparece sem descricao -- `_ler_descricao_motor` esta procurando "
        f"SKILL.md na arvore errada. Linhas: {linhas_de_motor}"
    )
