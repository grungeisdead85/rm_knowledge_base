# Making Fuel: tree bark dye research

Research pass, 2026-09-23. Feeds the tree dye generator (bark and log routes
for every tree, in vanilla's Make dye category).

## Rules (Jay's)

1. A tree with a vanilla BARK_DYE keeps vanilla's colour.
2. A tree with a documented bark dye gets the documented colour (table below).
3. Any other tree gets its own live WOOD colour (`state_color.Solid` of its WOOD
   material) as the default. This is read at runtime, so it covers trees added
   by other mods and modules with no curation.
4. A tree with no WOOD material has no logs and no bark, so it has nothing to
   make a bark dye from (abaca, banana).

## Method for a documented colour

- Source: the species' bark, as a dye, in dye literature, ethnobotany or
  textile studies. Other parts (hulls, peels, leaves, fruit) do not count for a
  bark dye; they are listed separately as notes.
- Reference condition: alum-mordanted or unmordanted results where given,
  since those are the plain results most sources report.
- Mapping: nearest of DF's 136 descriptor colours by name and shade, reusing
  vanilla's own choice where vanilla already named the same shade (alder's
  red-brown bark is RUSSET, so candlenut's red-brown inner bark is RUSSET).

## How vanilla chose its 22 bark dye colours

No published source. Patch 52.03 added 60+ outdoor plant dyes without naming
one. Spot checks show loose grounding in dye practice, not the standard
reference result:

- Apple bark: vanilla ROSE. Literature: yellow-brown to yellow-green with alum
  (CAMEO), lemon to intense yellow on cotton (Radomska 2022), rusty brown with
  copper; one study found yellowish-orange-red shades on linen.
- Alder bark: vanilla RUSSET. Literature: brown, red-brown and orange-red,
  widely used by North American tribes (USDA Forest Service).
- Walnut: vanilla gives it no dye at all, though walnut bark and hulls are among
  the best documented dyes there are. Coverage was selective, not exhaustive.

## Overrides (documented bark dyes)

| Tree | Documented bark result | DF colour | Sources |
|---|---|---|---|
| WALNUT | Juglone; rich colorfast brown; reddish-brown; warm deep taupes; darkest of the barks tested beside osage orange and red cedar | DARK_BROWN | northernwoodlands.org (Local color); Arifeen et al. 2021 (AGRIS); maiwa.com (black walnut); K-State McNair (Doty 2011) |
| CASHEW | Bark and fruit used for marking ink and colouring hair black | BLACK | PROSEA, Introduction to Dyes and tannins, Table 1 |
| MANGO | Bark used for dyeing cloth and matting yellow | YELLOW | PROSEA, Introduction to Dyes and tannins, Table 1 |
| CANDLENUT | Inner bark gives a red-brown dye (kapa, olona cordage) | RUSSET | Wikipedia, Aleurites moluccanus; Wehewehe (NEAL 506); canoeplants.com; mnbg.org |
| BAYBERRY | Bark (yamamomo kawa): light brown unmordanted, light yellowish brown with ash water, brown to black with iron; named colour in the Engi-shiki | LIGHT_BROWN | CAMEO, Uemura dye archive samples 11R, 12L, 13R |

Caveat on BAYBERRY: the record is Morella rubra (Chinese/Japanese bayberry).
DF's bayberry is not tied to a species in the raws.

## All 50 trees without a vanilla bark dye

"Default" means the tree's own WOOD colour, per rule 3.

| Tree | Kind | Bark record | Dye colour | Notes |
|---|---|---|---|---|
| ABACA | real, no WOOD | n/a | none | No logs or bark (rule 4) |
| BANANA | real, no WOOD | n/a | none | No logs or bark (rule 4); vanilla has leaf and peel dyes |
| CARAMBOLA | real | not found | default FLAX | Not searched individually |
| CASHEW | real | yes | BLACK | Override |
| COFFEE | real | not found | default TAUPE_PALE | Not searched individually; vanilla has bean dye |
| DURIAN | real | not found | default TAUPE_PALE | Not searched individually |
| PAPAYA | real | not found | default TAUPE_PALE | Not searched individually |
| PARADISE_NUT | real | not found | default LIGHT_BROWN | Not searched individually |
| RAMBUTAN | real | no colour | default BRONZE | Searched: young shoots dye yellow silk green; leaves and fruit walls used for black; bark only medicinal |
| TEA | real | not found | default TAUPE_PALE | Not searched individually; vanilla has leaf dye |
| AVOCADO | real | not found | default CHESTNUT | Not searched individually; vanilla has skin dye |
| LIME | real (citrus) | no | default TAN | Searched: citrus dye records are peels (yellow), not bark |
| POMELO | real (citrus) | no | default ASH_GRAY | As lime |
| CITRON | real (citrus) | no | default ASH_GRAY | As lime |
| ORANGE | real (citrus) | no | default BURNT_SIENNA | As lime |
| BITTER_ORANGE | real (citrus) | no | default TAUPE_PALE | As lime |
| FINGER_LIME | real (citrus) | no | default TAN | As lime |
| ROUND_LIME | real (citrus) | no | default TAN | As lime |
| DESERT_LIME | real (citrus) | no | default TAN | As lime |
| KUMQUAT | real (citrus) | no | default TAUPE_PALE | As lime |
| CUSTARD-APPLE | real | no | default TAN | Searched: leaves used in tanning, yield a blue or black dye; bark only medicinal |
| DATE_PALM | real | not found | default BURNT_SIENNA | Not searched individually |
| LYCHEE | real | not found | default TAUPE_SANDY | Not searched individually; PROSEA lists it only as a lac insect host |
| MACADAMIA | real | not found | default PALE_BROWN | Not searched individually |
| ALMOND | real | no | default COPPER | Searched: shells, stems, hulls and skins dye wool; no bark record; vanilla has shell dye |
| BAYBERRY | real | yes | LIGHT_BROWN | Override |
| GINKGO | real | not found | default PEACH | Not searched individually; vanilla has leaf dye |
| PECAN | real | no | default PEACH | Searched: hulls dye wool dark brown, cotton gray (CAMEO); no bark record |
| PERSIMMON | real | no | default TAN | Searched: fruit (kakishibu, vanilla has fruit dye), leaves, and black persimmon wood chips; no bark record |
| SAND_PEAR | real | not found | default BUFF | Not searched individually; the pear bark study found is Pyrus communis |
| WALNUT | real | yes | DARK_BROWN | Override |
| SAGUARO | real | not found | default ECRU | Not searched individually |
| CEDAR | real | weak | default OLIVE | Searched: western red cedar bark on alum wool gave only a faint, unnamed colour; DF's cedar species is unclear |
| KAPOK | real | not found | default TAN | Not searched individually |
| CANDLENUT | real | yes | RUSSET | Override |
| MANGO | real | yes | YELLOW | Override |
| RUBBER | real | not found | default FLAX | Not searched individually |
| CACAO | real | not found | default CHOCOLATE | Not searched individually |
| PALM (coconut) | real | no | default TAUPE_DARK | PROSEA: nuts dye silk green, fruit stalk colours teeth black; no bark record |
| TOWER_CAP | fantasy | n/a | default WHITE | |
| BLACK_CAP | fantasy | n/a | default BLACK | |
| NETHER_CAP | fantasy | n/a | default DARK_INDIGO | |
| GOBLIN_CAP | fantasy | n/a | default RED | |
| FUNGIWOOD | fantasy | n/a | default LEMON | |
| TUNNEL_TUBE | fantasy | n/a | default VIOLET | |
| SPORE_TREE | fantasy | n/a | default TEAL | |
| BLOOD_THORN | fantasy | n/a | default CRIMSON | |
| GLUMPRONG | fantasy | n/a | default PURPLE | |
| FEATHER | fantasy | n/a | default CREAM | |
| HIGHWOOD | fantasy | n/a | default (template) | Raws set no WOOD colour; the live WOOD_TEMPLATE colour is read at runtime |

Default colours above are the vanilla raws' WOOD `STATE_COLOR:ALL_SOLID`. The
generator reads the live material, so a mod that recolours a wood changes its
default dye with it.

## Gaps

16 real species were not searched individually in this pass (marked above).
They carry the default until a record turns up. Records for other parts of a
tree (hulls, peels, leaves, fruit, heartwood) are noted for any later non-bark
dyes; none of them sets a bark colour.

## Source links

- Patch 52.03: https://kitfoxgames.itch.io/dwarf-fortress/devlog/1004046/patch-5203
- DF wiki, Dye: https://dwarffortresswiki.org/index.php/Dye
- CAMEO, Apple bark: https://cameo.mfa.org/wiki/Apple_bark
- Radomska 2022, apple bark on cotton: https://agro.icm.edu.pl/agro/element/bwmeta1.element.agro-94740d3a-b8da-4d62-93bf-40e24649a631/c/35.pdf
- Fruit tree barks on linen (Ukraine): https://r2.donnu.edu.ua/items/43523c41-e535-44c6-a1c8-8f2d8a00d797/full
- USDA Forest Service, ethnobotany dyes: https://www.fs.fed.us/wildflowers/ethnobotany/dyes.shtml
- Northern Woodlands, walnut: https://northernwoodlands.org/articles/article/local_color_finding_wild_sources_for_dye_in_the_forest
- Arifeen et al. 2021, walnut bark juglone: https://agris.fao.org/search/fr/records/65df630f4c5aef494fe24ef5
- Maiwa, black walnut: https://maiwa.com/collections/black-walnut
- Doty 2011, osage, walnut and red cedar bark: https://www.k-state.edu/leadership/scholar-development-and-undergraduate-research/mcnair-scholars/scholars/alumni/kelsie_d.html
- PROSEA, Introduction to Dyes and tannins: https://uses.plantnet-project.org/en/PROSEA,_Introduction_to_Dyes_and_tannins
- Aleurites moluccanus (kukui): https://en.wikipedia.org/wiki/Aleurites_moluccanus
- Wehewehe, kukui: https://wehe.hilo.hawaii.edu/?q=kukui
- Canoe Plants, kukui: https://canoeplants.com/kukui.html
- CAMEO, Yamamomo kawa (bayberry) 12L: https://cameo.mfa.org/wiki/Yamamomo_kawa_(Bayberry)_-_left_(12_L)
- CAMEO, Yamamomo kawa (bayberry) 11R: https://cameo.mfa.org/wiki/Yamamomo_kawa_(Bayberry)_-_right_(11_R)
- CAMEO, Yamamomo Jyuhi (bayberry) 13R: https://cameo.mfa.org/wiki/Yamamomo_Jyuhi_(Bayberry)_-_right_(13_R)
- CAMEO, Pecan: https://cameo.mfa.org/wiki/Pecan
- NTBG, Annona reticulata: https://ntbg.org/database/plants/detail/annona-reticulata
- Singapore Infopedia, rambutan: https://eresources.nlb.gov.sg/infopedia/articles/SIP_208_2004-12-16.html
- Western red cedar bark dye: https://allfiberarts.com/red-cedar-dye/
- Persimmon (kakishibu): https://paper.gatech.edu/node/1175
- Black persimmon wood chips: https://kawasakigakuen.repo.nii.ac.jp/record/223/files/%EF%BC%AB%2013-066-072%E6%96%B0.pdf
- Almond by-products: https://hal.archives-ouvertes.fr/hal-03327804
- Citrus peel dyes: https://ppaspk.org/index.php/PPAS-A/article/view/1456
