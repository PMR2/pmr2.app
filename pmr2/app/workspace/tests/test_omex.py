from unittest import TestCase, TestSuite, makeSuite

from pmr2.app.workspace.omex import build_omex, _process, parse_manifest

demo_omex = '''<?xml version='1.0' encoding='utf-8' standalone='yes'?>
<omexManifest
    xmlns="http://identifiers.org/combine.specifications/omex-manifest">
  <content location="./manifest.xml"
    format="http://identifiers.org/combine.specifications/omex-manifest" />
  <content location="./BorisEJB.xml"
    format="http://identifiers.org/combine.specifications/sbml" />
  <content location="./paper/Kholodenko2000.pdf"
    format="application/pdf" />
  <content location="http://www.ebi.ac.uk/biomodels-main/BIOMD0000000010"
    format="http://identifiers.org/combine.specifications/sbml" />
  <content location="./metadata.rdf"
    format="http://identifiers.org/combine.specifications/omex-metadata" />
</omexManifest>'''


class TestOmex(TestCase):
    """
    Test Omex Core.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_manifest_load(self):
        results = parse_manifest(demo_omex)
        self.assertEqual(results,
            ['manifest.xml', 'BorisEJB.xml', 'paper/Kholodenko2000.pdf',
            'metadata.rdf'])


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOmex))
    return suite

