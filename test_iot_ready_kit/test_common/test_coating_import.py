from nose.tools import assert_equal

from iot_ready_kit.common.coating_import import CoatingImporter


def test_sum_up_coatings():
    data_string = """32819;P22_Protolab_Demokueche;P00_HE~9071645_KMP0,0;HE Kreuzmontageplatte, D=0mm mit vormontierten Euroschrauben, Stahl vernickelt;VPE200;9071645;9071645;;0;Hettich Kanban;1;1;0;0;0;0;;;;;;;;;;;;;;;;;;;;0;;15;0;0;0;0;1;16385;0;0;0;1;;;;;P00_HE_Sen110D_E19_F2,0_K0,0;P00_Topfscharnier_Holz_D
32821;P22_Protolab_Demokueche;P00_HE~9071645_KMP0,0;HE Kreuzmontageplatte, D=0mm mit vormontierten Euroschrauben, Stahl vernickelt;VPE200;9071645;9071645;;0;Hettich Kanban;1;1;0;0;0;0;;;;;;;;;;;;;;;;;;;;0;;15;0;0;0;0;1;16385;0;0;0;1;;;;;P00_HE_Sen110D_E19_F2,0_K0,0;P00_Topfscharnier_Holz_D
32823;P22_Protolab_Demokueche;P00_HE~9071645_KMP0,0;HE Kreuzmontageplatte, D=0mm mit vormontierten Euroschrauben, Stahl vernickelt;VPE200;9071645;9071645;;0;Hettich Kanban;1;1;0;0;0;0;;;;;;;;;;;;;;;;;;;;0;;15;0;0;0;0;1;16385;0;0;0;1;;;;;P00_HE_Sen110D_E19_F2,0_K0,0;P00_Topfscharnier_Holz_D
32825;P22_Protolab_Demokueche;P00_HE~9071645_KMP0,0;HE Kreuzmontageplatte, D=0mm mit vormontierten Euroschrauben, Stahl vernickelt;VPE200;9071645;9071645;;0;Hettich Kanban;1;1;0;0;0;0;;;;;;;;;;;;;;;;;;;;0;;15;0;0;0;0;1;16385;0;0;0;1;;;;;P00_HE_Sen110D_E19_F2,0_K0,0;P00_Topfscharnier_Holz_D
32774;P22_Protolab_Demokueche;P00_HE~70151_SoF_H100;HE Sockelverstellfu� Korrekt, H�he=100mm;Verstellbereich 74-110 mm;70151;70151;;0;Hettich Kanban;1;1;0;0;0;0;;;;;;;;;;;;;;;;;;;;0;;15;0;0;0;0;1;16387;0;0;0;1;;;;Sockelh�he 100 mm;P00_HE_SoF_S_H100_mS;P00_Sockelverstellfuss_L_R
32775;P22_Protolab_Demokueche;P00_HE~61854_Sockelhalter_mS;HE Sockelhalter zum Schrauben, mit Schrauben 4x35;;61854;61854;;0;Hettich Kanban;1;1;0;0;0;0;;;;;;;;;;;;;;;;;;;;0;;15;0;0;0;0;1;16387;0;0;0;1;;;;;P00_HE_SoF_S_H100_mS;P00_Sockelverstellfuss_L_R
32776;P22_Protolab_Demokueche;P00_HE~61855_Sockelclip_S;HE Sockelclip zum Schrauben;;61855;61855;;0;Hettich Kanban;1;1;0;0;0;0;;;;;;;;;;;;;;;;;;;;0;;15;0;0;0;0;1;16387;0;0;0;1;;;;;P00_HE_SoF_S_H100_mS;P00_Sockelverstellfuss_L_R"""
    rows = data_string.split('\n')
    rows = list(map(lambda row: row.split(';'), rows))
    coatings = CoatingImporter.sum_up_coatings(rows)

    assert_equal(coatings['16385']['P00_HE~9071645_KMP0,0']['count'], 4)
