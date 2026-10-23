"""Testes do coletor com dados de exemplo (sem internet): python3 -m unittest discover tests"""
import json, sys, tempfile, unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "kit" / "coletor"))
import coleta  # noqa: E402

FX = RAIZ / "tests" / "fixtures"
HOJE = date(2026, 9, 15)


class TestSinais(unittest.TestCase):
    def test_epoch_modelos(self):
        s = coleta.sinais_epoch_modelos(FX / "epoch_modelos.csv", HOJE)
        self.assertEqual(s["compute-fronteira"][0], 1e27)           # o antigo (2024) fica de fora
        self.assertAlmostEqual(s["lacuna-aberto-fechado"][0], 50)   # 1e27 / 2e25
        self.assertAlmostEqual(s["corrida-eua-china"][0], 20)       # 1e27 / 5e25
        self.assertIn("Fechado-A", s["compute-fronteira"][1])

    def test_clusters_ignora_planejado_e_excluido(self):
        v, donos = coleta.sinais_epoch_clusters(FX / "epoch_clusters.csv")["concentracao-clusters"]
        self.assertAlmostEqual(v, 90)                                # 900 de 1000
        self.assertTrue(donos.startswith("Dono1 · Dono2"))

    def test_aei_pega_o_mes_mais_recente(self):
        v, d = coleta.sinais_aei(FX / "aei.csv")["automacao-uso"]
        self.assertEqual(v, 48.62)
        self.assertIn("Brasil 44.1%", d)

    def test_aiid_deixa_de_fora_os_2_meses_recentes(self):
        v, _ = coleta.sinais_aiid(FX / "incidents.csv", HOJE)["incidentes-ia"]
        self.assertAlmostEqual(v, 2.0)                               # 6/mês ÷ 3/mês; agosto (50) não conta

    def test_limites(self):
        self.assertTrue(coleta.LIMIAR["compute-fronteira"][0](1e27))
        self.assertFalse(coleta.LIMIAR["automacao-uso"][0](48.62))
        self.assertTrue(coleta.LIMIAR["incidentes-ia"][0](2.0))

    def test_aiid_url_mais_nova(self):
        html = '<a href="https://x.r2.dev/backup-20261012101643.tar.bz2"> <a href="https://x.r2.dev/backup-20261019101022.tar.bz2">'
        self.assertTrue(coleta.aiid_mais_recente(html).endswith("20261019101022.tar.bz2"))


class TestPontaAPonta(unittest.TestCase):
    def test_main_grava_os_tres_arquivos(self):
        with tempfile.TemporaryDirectory() as d:
            coleta.main(["--estado", d, "--dados", str(FX), "--hoje", "2026-09-15"])
            js = json.loads((Path(d) / "sinais.json").read_text())
            self.assertEqual(len(js["sinais"]), 6)
            self.assertEqual(js["erros"], {})
            md = (Path(d) / "sinais.md").read_text()
            self.assertIn("**SIM**", md)
            self.assertIn("`delegacao-pessoal`", md)
            self.assertEqual(len((Path(d) / "historico.csv").read_text().splitlines()), 7)

    def test_ids_batem_com_sinais_yaml(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("pyyaml ausente")
        ids = {s["id"] for s in yaml.safe_load(open(RAIZ / "kit" / "cenarios" / "sinais.yaml"))["sinais"]}
        self.assertEqual(ids, set(coleta.LIMIAR) | set(coleta.MANUAIS) | set(coleta.PESSOAIS))


if __name__ == "__main__":
    unittest.main()
