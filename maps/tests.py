import json
from copy import deepcopy
from typing import List
from unittest import TestCase

from django.contrib.gis.geos import MultiPolygon, Polygon
from django.test import TestCase as DjangoTestCase
from django.urls import reverse

from .converter import encode_geometry, decode, Point
from .models import Region
from .factories import RegionFactory, INFOBOX, multipolygon_factory

POLYGON_JSON = """[
    [[-2.4610019,49.4612907],[-2.4610233,49.4613325],[-2.4628043,49.4608862],[-2.4634051,49.4606073],[-2.4640274,49.4606491],[-2.4642205,49.4599378],[-2.4651432,49.4597984],[-2.4651861,49.4587523],[-2.4658513,49.4584455],[-2.4653149,49.4574273],[-2.4653149,49.4564509],[-2.4643064,49.4562138],[-2.4639845,49.4557954],[-2.4626756,49.4559349],[-2.462461,49.4563533],[-2.4618816,49.4569531],[-2.4607658,49.456967],[-2.46068,49.4574691],[-2.4605298,49.4577063],[-2.46068,49.4578178],[-2.460444,49.4580828],[-2.4600363,49.4579434],[-2.4595642,49.4580828],[-2.4595213,49.4583339],[-2.4594784,49.458836],[-2.4592209,49.4590452],[-2.4592209,49.4593242],[-2.4590921,49.4595055],[-2.4593067,49.4597147],[-2.4596715,49.4599239],[-2.45965,49.4602168],[-2.4598861,49.4603981],[-2.4602509,49.4604678],[-2.4603367,49.460677],[-2.4608088,49.4609002],[-2.4610019,49.4612907]],
    [[-2.4636197,49.4623646],[-2.4636412,49.4626086],[-2.4640059,49.4627411],[-2.4646497,49.4634384],[-2.4650359,49.4632292],[-2.4655938,49.4631734],[-2.4655402,49.462769],[-2.4655831,49.4624761],[-2.4647677,49.4621205],[-2.4640918,49.4624831],[-2.4636197,49.4623646]], 
    [[-2.4571201, 49.4784076], [-2.4573483, 49.4786237], [-2.4574685, 49.4789531], [-2.4576661, 49.4796136], [-2.4577769, 49.479622], [-2.4579404, 49.4796674], [-2.4578287, 49.4797392], [-2.4573783, 49.4798821], [-2.4566183, 49.4801498], [-2.4559938, 49.4804012], [-2.4554324, 49.4805623], [-2.454818, 49.4806346], [-2.4542875, 49.480678], [-2.4539084, 49.4806921], [-2.4531289, 49.4808192], [-2.4529168, 49.480814], [-2.4526488, 49.4809046], [-2.4522442, 49.4810096], [-2.4520445, 49.4811791], [-2.4520249, 49.481285], [-2.4519439, 49.4813545], [-2.4518445, 49.4813196], [-2.4517827, 49.4812476], [-2.4515704, 49.4812846], [-2.4514842, 49.4813645], [-2.4512999, 49.4813806], [-2.4506774, 49.4817428], [-2.4503135, 49.481942], [-2.4494686, 49.4823831], [-2.4490335, 49.4825497], [-2.4484615, 49.4828144], [-2.4482225, 49.4828864], [-2.4481007, 49.4828877], [-2.4480465, 49.4828135], [-2.4480259, 49.4826377], [-2.4480133, 49.4818683], [-2.448018, 49.4810642], [-2.4479555, 49.4804399], [-2.4482537, 49.4796809], [-2.4483429, 49.4795252], [-2.4482253, 49.4792213], [-2.4482399, 49.4786712], [-2.4482064, 49.4781907], [-2.4483126, 49.4778989], [-2.4484597, 49.4777901], [-2.4484136, 49.477678], [-2.4483672, 49.4775401], [-2.4484039, 49.4773617], [-2.4480329, 49.4768498], [-2.4479199, 49.4767788], [-2.4476557, 49.4767865], [-2.447567, 49.4766705], [-2.4474236, 49.4766155], [-2.4473732, 49.4765931], [-2.4474083, 49.4765395], [-2.4471471, 49.4764248], [-2.4469861, 49.4763692], [-2.4470452, 49.476239], [-2.4469725, 49.4761834], [-2.4468822, 49.4761821], [-2.4467092, 49.4760005], [-2.4466628, 49.4758876], [-2.4465464, 49.4758493], [-2.4462351, 49.4755649], [-2.4462193, 49.4754428], [-2.4460519, 49.475307], [-2.4458935, 49.4752481], [-2.4456376, 49.475213], [-2.4454626, 49.4752894], [-2.44528, 49.4751936], [-2.4454094, 49.4751541], [-2.4453195, 49.4750973], [-2.4450394, 49.4750927], [-2.4450724, 49.4749998], [-2.4450008, 49.4749285], [-2.4449018, 49.4749652], [-2.4447922, 49.4750201], [-2.4445263, 49.4749277], [-2.4442491, 49.4746626], [-2.4440592, 49.4744294], [-2.4442098, 49.4742298], [-2.4444498, 49.474157], [-2.4446586, 49.4741544], [-2.4447557, 49.474126], [-2.4447659, 49.4739592], [-2.4448508, 49.4738927], [-2.4449242, 49.473789], [-2.4448968, 49.4734142], [-2.4446687, 49.4734246], [-2.44457, 49.4733309], [-2.4442849, 49.4732477], [-2.444004, 49.4730522], [-2.4436335, 49.4728331], [-2.4435671, 49.4726301], [-2.4436457, 49.4724996], [-2.4436173, 49.4723754], [-2.4435125, 49.4723456], [-2.4434779, 49.4722847], [-2.4435768, 49.4722202], [-2.4435313, 49.4719107], [-2.4433953, 49.471812], [-2.4430519, 49.4717497], [-2.4427829, 49.4712845], [-2.4425933, 49.4710922], [-2.4425306, 49.4710278], [-2.4423757, 49.4708555], [-2.4419591, 49.4706456], [-2.4417293, 49.4706151], [-2.4416829, 49.4707236], [-2.4415384, 49.4707745], [-2.4414168, 49.4707741], [-2.441206, 49.470583], [-2.440916, 49.4702374], [-2.4410162, 49.4701953], [-2.4412927, 49.4703756], [-2.4413515, 49.4703468], [-2.4412372, 49.4700904], [-2.4413283, 49.4695613], [-2.4414129, 49.4695905], [-2.4414796, 49.4696136], [-2.4416092, 49.4696584], [-2.4418162, 49.4696711], [-2.4420932, 49.4694322], [-2.4426223, 49.4691965], [-2.4428, 49.4689855], [-2.4430456, 49.4688741], [-2.4429367, 49.4687015], [-2.4431746, 49.4684222], [-2.4433897, 49.4683247], [-2.4436481, 49.4683391], [-2.4437036, 49.4684119], [-2.4437942, 49.4683891], [-2.4437232, 49.4682506], [-2.443834, 49.468192], [-2.4441673, 49.4682828], [-2.4441217, 49.4681052], [-2.4438547, 49.4680182], [-2.443945, 49.4678936], [-2.4435627, 49.4672109], [-2.4431377, 49.4670663], [-2.4431663, 49.4668342], [-2.4434808, 49.4665466], [-2.4438509, 49.4665623], [-2.4441217, 49.4667018], [-2.4443358, 49.466695], [-2.444397, 49.466722], [-2.4447249, 49.4668667], [-2.4446987, 49.4667722], [-2.4448679, 49.4668292], [-2.4448264, 49.4666946], [-2.4448784, 49.4663931], [-2.4448656, 49.466306], [-2.4448894, 49.4660553], [-2.4449991, 49.4659415], [-2.4449633, 49.4658162], [-2.4445813, 49.4658614], [-2.4444221, 49.4656736], [-2.4444654, 49.4654606], [-2.444689, 49.4650443], [-2.4449472, 49.4645733], [-2.4453936, 49.4642472], [-2.4457539, 49.464235], [-2.4460702, 49.4644566], [-2.4460216, 49.4645216], [-2.4462346, 49.4645166], [-2.4463523, 49.4648235], [-2.4465649, 49.4645123], [-2.4470003, 49.4645893], [-2.4472787, 49.4645113], [-2.4474093, 49.4645435], [-2.4475603, 49.464504], [-2.4476684, 49.4644352], [-2.4479186, 49.4643795], [-2.4484632, 49.4640853], [-2.4485955, 49.4637732], [-2.4492588, 49.4635185], [-2.4494561, 49.463315], [-2.449897, 49.4633076], [-2.4503404, 49.4631088], [-2.4507199, 49.4629095], [-2.4512739, 49.4627643], [-2.4517935, 49.4629066], [-2.4520413, 49.4630266], [-2.4520597, 49.4632368], [-2.4515582, 49.4636523], [-2.4519084, 49.463778], [-2.4521928, 49.4640878], [-2.4520212, 49.4640928], [-2.4520245, 49.4641483], [-2.4524403, 49.4643669], [-2.4527633, 49.4645373], [-2.4527749, 49.464682], [-2.4529999, 49.4650521], [-2.453064, 49.4652718], [-2.4530511, 49.4654761], [-2.4532261, 49.4655634], [-2.4533776, 49.4658291], [-2.4533473, 49.4659621], [-2.453253, 49.4661648], [-2.4528583, 49.466388], [-2.4528159, 49.46661], [-2.4528965, 49.4666673], [-2.4529304, 49.4667641], [-2.4532166, 49.467311], [-2.4533664, 49.4674415], [-2.4536676, 49.4678156], [-2.4537024, 49.4684607], [-2.4538105, 49.4686638], [-2.4539438, 49.4687962], [-2.4536275, 49.4692433], [-2.4536049, 49.4692752], [-2.4536648, 49.4694478], [-2.4538138, 49.4696038], [-2.4538577, 49.4696214], [-2.4539237, 49.4696948], [-2.4543496, 49.4701684], [-2.4542832, 49.4701903], [-2.4542109, 49.4702141], [-2.4537587, 49.4696894], [-2.453371, 49.4696787], [-2.4533576, 49.4698357], [-2.4537104, 49.4698485], [-2.4536963, 49.4698259], [-2.4537486, 49.4698244], [-2.453791, 49.4698849], [-2.4533455, 49.4698688], [-2.4532775, 49.4698859], [-2.4532873, 49.4697329], [-2.4532908, 49.4696776], [-2.4529192, 49.4697207], [-2.4528965, 49.469707], [-2.4527424, 49.4697363], [-2.4525687, 49.4698799], [-2.4524314, 49.4700745], [-2.4523991, 49.4702141], [-2.4522864, 49.4703738], [-2.4521762, 49.4704659], [-2.4520393, 49.4706746], [-2.4520378, 49.4707459], [-2.4519929, 49.4708398], [-2.4519536, 49.4712042], [-2.4521369, 49.471928], [-2.4526147, 49.4726114], [-2.4526345, 49.4727151], [-2.4530523, 49.4731392], [-2.4535177, 49.473552], [-2.453601, 49.47373], [-2.4535895, 49.4738806], [-2.4538338, 49.4743972], [-2.4539392, 49.4745435], [-2.453971, 49.4748069], [-2.4540474, 49.4749275], [-2.454247, 49.4753059], [-2.4546873, 49.4759398], [-2.455336, 49.4767515], [-2.4560594, 49.4774702], [-2.45622, 49.4774771], [-2.4564876, 49.4775726], [-2.4567305, 49.4777363], [-2.45691, 49.4778896], [-2.4569745, 49.478118], [-2.4569744, 49.4782347], [-2.4571201, 49.4784076]]
]"""  # pylint: disable=line-too-long

FULL_ENCODE = [
    'al{lHft_NGBxAbJv@vBGzBlCf@ZvDnEF|@dCjEkB`E?n@iErA_A[eGsAi@wBsBA_FcBOo@_@U^u@o@ZqA[}Aq@GcBIi@q@w@?c@Yi@h@i@hAy@Cc@l@MhAi@Nm@|AmAf@',  # pylint: disable=line-too-long
    'wr{lHpd`No@D[fAiC~Bh@lAHnBpAIx@FdAcDgAeCV_B',
    '_w~lH~{~Mk@j@aAVcCf@ATG`@MW]yAs@wCs@{B_@oBM{BGiBCkAW{C?i@Qu@SoAa@g@UCMOFSLKGi@OQCe@gA{Bg@gAwAiD_@uAu@qBMo@?WLKb@CxCA~C?|BKtCz@^Pz@WlB@~AEz@TRZVGXIb@FfBiALWAs@TQJ[BIJDTs@J_@XJHM?Qb@c@VGFWv@}@VCZ_@J_@Ds@Ma@Pc@FVJQ?w@RFLMGSKURu@r@w@n@e@f@\\Ln@?h@DR`@@JPTLhAEAm@PQPy@d@w@j@iAf@MZNVEDSJGJR|@GR[LcAzAu@d@e@LK`@_@h@sADm@UGI]?Wd@i@dAy@FRc@v@DJp@WhBPEPCJGXCh@n@v@n@hBh@b@Tn@`@Uv@n@Rh@Ar@OJDPXMJTQ`Ab@GPu@VPfCkA\\uAl@Dx@~@ChA[t@@h@EJ[`APEI`@XGz@HPAp@BTTXEIkAd@_@h@FrAj@|Ar@`AxA@fAk@~@MI@h@}@V|@h@MvALt@EXF^LRJp@x@lB|@Xr@bCf@f@@vAf@xAf@hAZnB[fBWp@i@@sAcBWdA}@x@Aa@I?k@rAa@~@]@iAj@k@Lg@AQ`@s@\\[Eg@Qk@oAm@GINSFmBv@Y\\iAz@aCFg@TYXyA_AECa@J_@\\CFML}ArAEKCMhB{A@kA_@CAfABC?HKHByACM\\@J@IkABCE][c@g@Y[G_@UQUi@[M?QGiAGoCb@iC~ASBsArAsAzAc@P]CeBp@]Rs@FWLkAf@}BvAcD`CoCnC?`@Sr@_@p@]b@m@JW?a@\\'  # pylint: disable=line-too-long
]


class DecoderTestCase(TestCase):
    maxDiff = None
    points: List[List[Point]]
    islands: List[Polygon]

    @classmethod
    def setUpClass(cls):
        cls.points = json.loads(POLYGON_JSON)
        cls.islands = [Polygon(island) for island in cls.points]

    def test_encode_multipolygon(self):
        polygon = MultiPolygon(self.islands)
        self.assertEqual(FULL_ENCODE, encode_geometry(polygon))
        self.assertEqual(len(encode_geometry(polygon, min_points=20)), 2)

    def test_encode_polygon(self):
        polygon = self.islands[0]
        self.assertEqual(FULL_ENCODE[0], encode_geometry(polygon)[0])

    def test_decode(self):
        for i, point in enumerate(decode(FULL_ENCODE[1])):
            self.assertLess(abs(self.points[1][i][0] - point[0]), 0.00001)
            self.assertLess(abs(self.points[1][i][1] - point[1]), 0.00001)


class RegionTestCase(DjangoTestCase):
    region: Region

    @classmethod
    def setUpTestData(cls):
        cls.region = RegionFactory(polygon=multipolygon_factory())

    def test_full_info(self):
        infobox = deepcopy(INFOBOX)
        del infobox['geonamesID']
        del infobox['capital']['id']
        infobox['marker'] = {'lat': 12.516, 'lng': -70.033}

        response = self.client.get(reverse('region', args=(self.region.pk,)))
        self.assertEqual(response.status_code, 200)
        content = response.json()
        self.assertEqual(content['id'], self.region.pk)
        self.assertEqual(len(content['polygon']), 2)  # 2 islands
        self.assertDictEqual(content['infobox'], infobox)
