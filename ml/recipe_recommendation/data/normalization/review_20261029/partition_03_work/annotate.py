import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = json.loads((ROOT / 'partition_03.json').read_text(encoding='utf-8'))
M = {}
NOTES = {}

def add(block):
    for line in block.strip().splitlines():
        index, expr = line.split(' ', 1)
        index = int(index)
        assert index not in M, index
        M[index] = expr

add('''
0 smoked_milkfish
1 cooked_linguine_noodles
2 ginger
3 pork_leg
4 celery_stalk
5 thawed_mixed_vegetables
6 ripe_guava
7 young_coconut_meat
8 boiled_beef_tripe
9 pork_adobo
10 chicken_thigh&chicken_drumsticks
11 shrimp_fried_rice
12 fish_sauce
13 beef_powder|beef_bouillon_cube
14 raw_peanut
15 boiled_pork_heart&boiled_pork_lung&water&white_vinegar&ginger
16 canned_spicy_tuna
17 knorr_sinigang_sa_sampaloc_mix
18 canned_pineapple_tidbit_in_syrup
19 lemon_lime_soda
20 pork_inasal
21 lemongrass
22 coconut_milk_powder&water
23 firm_tofu
24 tikoy
25 seasoning_powder|broth_cube
26 beef_bouillon_cube
27 red_bell_pepper
28 canned_sardine_in_oil
29 bok_choy
30 bok_choy|pechay
31 spinach|moringa_leaves
32 green_onion
33 kangkong
34 kangkong
35 lemongrass
36 pechay
37 spring_onion
38 pechay_tagalog
39 kangkong
40 alugbati_leaves
41 misua_noodles
42 yard_long_bean
43 bok_choy
44 lemon_lime_soda
45 canned_red_kidney_bean
46 canned_water_chestnut
47 canned_coconut_milk
48 canned_crushed_tomato
49 canned_water_chestnut
50 canned_sisig
51 carrot
52 whole_chicken
53 chicken_bouillon_cube
54 yard_long_bean
55 chicken_bouillon_cube
56 cucumber
57 ampalaya
58 cooked_bamboo_shoot
59 bottled_crab_fat
60 calamansi_juice|(lime_juice&orange_juice)
61 peeled_chestnut
62 chorizo_de_bilbao
63 canned_corned_beef
64 crushed_pineapple
65 dried_anchovy
66 dry_mung_bean
67 fresh_breadcrumb_from_pandesal
68 sauteed_shiitake_mushroom&salt&pepper_unspecified_type
69 frozen_green_pea
70 yard_long_bean
71 green_bell_pepper
72 heavy_cream
73 blanched_yard_long_bean
74 miso_paste
75 mustard_leaves
76 red_bell_pepper&green_bell_pepper
77 unsalted_peanut
78 pigeon_pea
79 canned_pineapple_juice
80 potato&water
81 reserved_beef_broth
82 salted_egg_salsa
83 sharp_cheddar_cheese
84 shrimp
85 shrimp|dried_shrimp
86 cooked_squid
87 blanched_yard_long_bean
88 taro_root
89 uncooked_mung_bean
90 unsweetened_peanut_butter
91 water
92 kangkong
93 winged_bean
94 wood_ear_mushroom
95 young_coconut_meat
96 daikon
97 egg&salt&pepper_unspecified_type
98 ginger
99 green_bell_pepper
100 green_bell_pepper
101 green_bell_pepper
102 green_bell_pepper
103 green_papaya
104 broccoli
105 garlic
106 garlic
107 garlic
108 lettuce
109 beef_chuck
110 ground_lean_pork
111 unripe_jackfruit
112 baguio_bean
113 beef_rib
114 boneless_beef_rib|beef_brisket
115 beef_sirloin
116 boneless_bangus_belly
117 chicken_leg|chicken_thigh
118 chicken
119 boneless_chicken_thigh_fillet
120 chicken_breast_fillet
121 dressed_duck
122 shell_on_green_mussel
123 heart_of_palm
124 lechon_kawali
125 fish_unspecified_species
126 pompano
127 pork_belly
128 pork_knuckle
129 pork_meat&pork_fat
130 pork
131 pork_spare_rib_tip
132 pork_jowl
133 pork_belly
134 pork_ham
135 shelled_prawn
136 shrimp
137 tamarind
138 unripe_jackfruit
139 beef_short_rib
140 boneless_country_style_pork_rib|pork_belly
141 pork&pork_intestine
142 shelled_shrimp&shrimp_head&shrimp_shell
143 squid&squid_ink
144 knorr_beef_cube
145 bok_choy
146 canned_pineapple
147 carrot
148 carrot
149 boiled_chicken_breast
150 whole_grouper
151 onion
152 orange_sweet_potato
153 whole_pompano
154 potato
155 roma_tomato
156 whole_tilapia
157 white_onion
158 beef_small_intestine
159 ground_beef
160 pork_liver|beef_liver
161 pork_neck_bone
162 shelled_apple_snail
163 grilled_pork_belly
164 roast_chicken
165 crispy_pata_meat
166 dried_bihon_noodle
167 pork_loin
168 beef_steak
169 coconut_water
170 ginger
171 ampalaya&sea_salt&water
172 bell_pepper
173 carrot
174 green_bell_pepper
175 milkfish_steak
176 onion
177 red_bell_pepper&green_bell_pepper
178 red_bell_pepper
179 red_onion
180 patola
181 tomato
182 white_onion
183 white_onion|yellow_onion
184 yellow_onion|white_onion
185 milkfish
186 lemongrass
187 dried_banana_blossom&water
188 unseasoned_nori
189 snow_pea
190 tomato_garlic_prawn_sauce_mix
191 wood_ear_mushroom&water
192 bean_sprout
193 cornstarch_noodle|rice_stick_noodle
194 maggi_sinigang_sampaloc_with_gabi_mix
195 chicken_breast
196 garlic
197 beef_bouillon_cube
198 beef_bouillon_cube|pork_bouillon_cube|beef_powder
199 celery_stalk
200 napa_cabbage
201 frozen_pizza_dough
202 siling_pangsigang
203 sweet_potato
204 knorr_pork_cube
205 long_green_chili
206 pork_bouillon_cube
207 red_bell_pepper
208 knorr_shrimp_cube
209 white_onion
210 red_onion
211 ripe_guava|semi_ripe_guava
212 ground_beef
213 eden_cheese|quick_melt_cheese
214 ground_beef
215 beef_honeycomb_tripe
216 mixed_seafood
217 salmon_belly
218 winged_bean
219 unripe_tamarind
220 white_radish
221 red_bell_pepper
222 red_bell_pepper
223 red_bell_pepper
224 red_bell_pepper
225 tamarind_sinigang_mix
226 ensaladang_talong
227 pork_adobo_paksiw
228 siling_labuyo
229 tenderized_pork_belly
230 bell_pepper
231 kalabasa
232 chorizo
233 green_bell_pepper
234 cabbage
235 onion
236 raisin
237 white_radish
238 red_bell_pepper
239 red_bell_pepper
240 singkamas
241 white_onion
242 lemongrass
243 green_onion
244 sweet_corn
245 all_purpose_flour
246 raisin
247 apple_cider_vinegar
248 chili_flake
249 cooking_oil
250 fish_sauce
251 garlic&salt
252 ginger
253 ginger
254 canned_jalapeno_pepper
255 turmeric
256 tamarind_soup_base_mix
257 sauteed_shrimp_paste
258 siling_labuyo
259 sugar
260 tomato_paste
261 water
262 red_chili_flake|sriracha_hot_chili_sauce
263 soy_sauce
264 annatto_powder|(annatto_seed&water)
265 cinnamon
266 fresh_rosemary
267 five_spice_powder
268 liquid_pork_seasoning
269 roasted_peanut
270 sake
271 sugar
272 white_sugar
273 breadcrumb
274 pork_leg
275 grilled_tomato
276 unripe_jackfruit
277 white_radish
278 whole_milkfish
279 whole_chicken
280 whole_chicken
281 whole_chicken
282 whole_chicken
283 grated_coconut
284 garlic
285 garlic
286 garlic
287 garlic
288 !source_issue
289 whole_pork_leg
290 whole_spring_chicken
291 yellow_bell_pepper
292 tamarind_sinigang_mix
293 chicken_wing|chicken_thigh|mixed_chicken_parts
294 pork
295 pork_leg
296 pork_chop
297 sotanghon_noodles
298 napa_cabbage
299 annatto_seed
''')
add('''
300 annatto_seed&water
301 banana_ketchup|tomato_ketchup
302 tamarind_paste
303 cabbage
304 chicken_stock
305 lemon_lime_soda
306 cornstarch
307 fried_dried_fish
308 fried_dried_fish
309 glutinous_rice
310 yard_long_bean
311 canned_green_pea
312 japanese_rice_vinegar
313 lemon_lime_soda
314 liver_spread
315 longganisa
316 mayonnaise
317 tomato
318 palm_vinegar
319 peanut
320 chili_leaves
321 pork
322 pork_chicharon
323 @context
324 processed_cheese
325 spiced_vinegar
326 smoked_round_scad
327 spiced_vinegar
328 shrimp_stock
329 sweet_chili_sauce
330 preserved_sweetened_jackfruit
331 smoked_fish
332 ube
333 water
334 white_miso_paste|yellow_miso_soybean_paste
335 green_bell_pepper
336 chicken_breast_fillet|mixed_chicken_parts
337 anchovy
338 beef_shoulder_clod
339 beef_brisket|beef_meat_cube
340 beef_shank|pork_shank
341 chicken_fillet
342 chicken
343 chicken_liver
344 round_scad
345 ripe_guava
346 half_shell_mussel
347 pork_round
348 pork_belly
349 potato
350 salmon_head
351 shelled_shrimp_with_head_and_tail
352 beef_sirloin
353 tilapia_fillet
354 beef_sirloin_steak
355 mud_crab_leg|mud_crab_claw
356 unripe_jackfruit
357 cooked_shelled_shrimp
358 pancit_canton_noodle
359 pork_belly
360 napa_cabbage
361 tahure
362 baby_potato
363 pork_belly|pork_butt
364 pork_lung
365 red_bell_pepper
366 red_onion&water&salt
367 yellow_bell_pepper
368 five_spice_powder
369 black_pepper
370 pepper_unspecified_type
371 salt
372 whole_chicken
373 bottled_olive
374 soy_sauce
375 white_vinegar
376 ground_bay_leaf|bay_leaf
377 beef_bouillon_cube
378 beef_bile
379 calamansi_juice
380 calamansi_juice|lemon_juice
381 roasted_cashew
382 chicken_gizzard
383 cooking_oil
384 fried_dried_fish
385 dried_shrimp&water
386 soy_sauce
387 pitted_green_olive
388 !source_issue
389 lemon_lime_soda
390 thai_basil_leaves
391 cooking_oil
392 cooking_oil
393 olive_oil
394 red_wine_vinegar|cane_vinegar
395 pork_floss
396 shrimp_juice
397 spanish_olive
398 toasted_garlic
399 water
400 white_vinegar
401 pork_fat
402 beef_shank
403 chicken_breast_fillet
404 clam&water
405 suahe_shrimp
406 pork_belly
407 spinach
408 boiled_chicken_breast
409 pork_liver
410 chicken_liver
411 ground_pepper_unspecified_type
412 cayenne_pepper_powder
413 red_pepper_flake
414 yellow_bell_pepper
415 kalabasa
416 lemon_balm
417 cooking_oil
418 kamias|frozen_kamias
419 nori
420 steamed_shelled_shrimp
421 fish_fillet
422 taro_leaves
423 pork_belly
424 chili_leaves
425 dried_taro_leaves
426 roast_chicken_drippings
427 milk|water
428 !source_issue
429 prime_rib_roast
430 onion
431 garlic
432 violet_sticky_rice
433 pork_blood
434 water
435 chicken_drumsticks
436 bacon
437 bulalo_broth
438 yard_long_bean
439 deep_fried_tofu
440 dried_chili&water
441 katuray_flower
442 tamarind|tamarind_base_powder
443 calamansi|lime
444 bagoong_unspecified_type
445 glutinous_rice
446 unripe_tamarind
447 beef_stock|(beef_bouillon_cube&water)
448 white_miso_paste
449 ready_made_ramen_noodles
450 low_sodium_spam
451 milkfish_belly_fillet
452 firm_tofu
453 bok_choy
454 bok_choy
455 pechay
456 pechay_tagalog
457 canned_baked_bean
458 skinless_chicken_breast_fillet
459 garlic
460 corn
461 corn_on_cob
462 chicken_bouillon_cube
463 lechon_sauce
464 beef_stock|beef_bouillon_cube
465 canned_applesauce
466 pork_chicharon_with_meat
467 chicken_stock|water
468 first_press_coconut_milk
469 cornstarch
470 eggplant
471 grated_coconut
472 japanese_rice
473 kangkong_leaves
474 cooked_miki_lucban_noodle
475 mung_bean
476 papaya
477 uncooked_red_rice
478 rice_washing_water
479 smoked_coconut_cream
480 sweet_potato_leaves
481 water
482 winged_bean
483 food_coloring&jackfruit_flavoring
484 red_food_coloring
485 sweet_corn
486 hard_boiled_egg
487 long_green_chili
488 green_onion
489 garlic
490 jalapeno_pepper
491 squid
492 bone_in_pork_belly
493 marinated_goat_meat
494 boneless_pork_belly
495 carrot
496 buttered_toasted_pandesal
497 chicken_breast
498 seasoned_yellow_rice
499 beef_chuck
500 tulingan
501 lechon
502 pampanga_longganisa
503 round_scad
504 tuna_jaw
505 lemon_juice
506 maggi_magic_chicken_cube
507 carrot
508 eggplant
509 potato
510 red_onion
511 squid
512 tomato
513 salted_duck_egg
514 dried_taro_leaves
515 chili_leaves
516 pork_ear
517 sole_fillet|white_fish_fillet
518 siling_labuyo
519 chicken_bouillon_cube
520 coconut_water&coconut_meat
521 dried_fish|labahita_fillet
522 deep_fried_firm_tofu
523 ginger
524 green_papaya
525 jalapeno_pepper
526 knorr_chicken_cube
527 long_green_chili
528 long_red_chili|thai_chili
529 poppy_seed_hotdog_bun
530 siling_labuyo
531 saba_banana
532 siling_labuyo
533 skinned_squid_with_tentacle
534 !source_issue
535 wood_ear_mushroom&water
536 beef_bottom_round|beef_top_round
537 boneless_skinless_chicken_thigh_meat|boneless_skinless_chicken_leg_meat
538 beef_sirloin|beef_top_round
539 boneless_skinless_chicken_thigh_meat|boneless_skinless_chicken_breast
540 shucked_oyster
541 thawed_half_shell_mussel
542 shucked_oyster
543 pork_belly_with_ribs|pork_spare_rib
544 pork_face&pork_ear
545 pork_sirloin
546 pork_spare_rib
547 beef_ribeye_steak
548 tuna_belly
549 red_finger_chili
550 red_onion
551 salted_egg
552 siling_labuyo
553 pork_belly
554 carrot
555 orange_sweet_potato
556 chili_leaves
557 sweet_potato
558 fried_firm_tofu
559 tahure
560 green_onion_leaves
561 leek
562 spring_onion
563 calamansi_juice|lemon_juice
564 cooking_oil
565 bottled_jalapeno_pepper
566 calamansi_juice|lemon_juice
567 !source_issue
568 coconut_oil
569 cornstarch&water
570 fish_sauce|salt
571 heavy_cream
572 korean_hot_pepper_paste
573 maggi_savor_seasoning_sauce
574 leek
575 fish_sauce
576 black_peppercorn
577 pineapple_juice
578 coarse_salt
579 sauteed_shrimp_paste
580 sugar
581 rehydrated_wood_ear_mushroom
582 eggplant
583 annatto_powder&water
584 fresh_tarragon_leaves
585 kosher_salt
586 !source_issue
587 thai_chili
588 !source_issue
589 ginger
590 dried_shrimp
591 siling_labuyo
592 white_onion
593 skin_on_chicken_breast_fillet
594 green_finger_chili
595 whole_tilapia
596 moringa_leaves
597 green_finger_chili
598 fermented_fish_sauce
599 !source_issue
''')
add('''
600 long_grain_purple_rice
601 toasted_belacan
602 lumpia_wrapper
603 calamansi_juice
604 lumpia_wrapper
605 calamansi_juice
606 speck|etag
607 fried_firm_tofu
608 shelled_shrimp
609 buttercup_squash
610 baguio_bean
611 lumpia_wrapper
612 pork_shoulder
613 ground_beef_round
614 unripe_tamarind&water
615 uncooked_penne_noodle
616 shelled_shrimp_with_head_and_tail
617 firm_tofu
618 garlic
619 corn
620 first_press_coconut_milk
621 day_old_cooked_rice
622 young_pineapple
623 cooked_long_grain_rice
624 sweet_potato
625 kangkong
626 sunny_side_up_egg
627 finger_chili
628 hard_boiled_egg
629 jalapeno_pepper
630 beef_shank_with_marrow_bone
631 oxtail
632 pork_leg
633 napa_cabbage
634 eggplant
635 potato
636 long_green_chili
637 taro_root
638 skin_on_boneless_bangus
639 corn
640 fried_extra_firm_tofu
641 green_chili
642 green_finger_chili
643 breadnut
644 long_green_chili
645 pork_chop
646 spanish_mackerel_steak
647 vienna_sausage
648 boneless_skinless_chicken_thigh_meat
649 chicken_feet
650 chicken_wing_drumettes_and_flats|mixed_chicken_parts
651 tripe
652 pork_back_rib
653 unripe_jackfruit
654 ripe_mango
655 saba_banana
656 siling_labuyo
657 lemongrass
658 lemongrass
659 five_spice_powder
660 bagoong_alamang|guinamos
661 sherry|shaoxing_wine
662 garlic_powder
663 miso_paste
664 coconut_sap_vinegar
665 melted_unsalted_butter
666 cooking_oil
667 green_pickle_relish
668 !source_issue
669 beef_shank&beef_bones
670 siling_labuyo
671 white_onion
672 star_anise
673 plantain
674 spanish_chorizo
675 button_mushroom
676 frozen_shelled_shrimp
677 salted_dried_fish
678 roasted_white_onion
679 barbecue_sauce
680 ground_pork|ground_beef
681 canned_mackerel_in_brine
682 white_kidney_bean&water
683 uncooked_pancit_canton_noodle
684 sashimi_grade_tuna
685 cauliflower
686 pandan_leaves
687 garlic
688 calamansi_juice
689 garlic
690 cooked_chicken
691 day_old_cooked_rice|freshly_cooked_rice
692 cooked_jasmine_rice
693 potato
694 rice_washing_water
695 hard_boiled_egg
696 filipino_hotdog
697 green_cardamom_pod
698 hard_boiled_egg
699 fish_belly_fillet
700 skinned_squid_mantle
701 lemongrass_bulb
702 siling_pangsigang
703 potato
704 glutinous_white_corn
705 pandan_leaves
706 saba_banana
707 siling_labuyo
708 marinated_thawed_boneless_bangus
709 chicken_breast&chicken_leg
710 fried_dried_fish
711 fried_round_scad
712 long_green_chili
713 lamb_shank
714 long_green_chili
715 salted_round_scad
716 pechay
717 siling_labuyo
718 siling_pangsigang
719 !source_issue
720 fried_tuyo
721 skinless_pork_chop
722 red_finger_chili
723 pineapple
724 salted_egg_yolk
725 taro_root
726 !source_issue
727 cilantro
728 cornstarch&pork_broth
729 garlic_flake
730 peanut
731 ilocos_vinegar
732 tamarind_pod
733 !source_issue
734 green_chili
735 romaine_lettuce
736 boneless_whole_bangus
737 green_finger_chili
738 desiccated_coconut
739 pork_loin
740 coconut_milk
741 winged_bean
742 bok_choy
743 pork_shoulder
744 siling_labuyo
745 chicken_wing&chicken_wing_tip
746 longganisa
747 sweet_pepper
748 uncooked_dried_danggit
749 coconut_milk_powder
750 tilapia_fillet
751 corn_kernel
752 cooked_angel_hair_spaghetti
753 beef_brisket|beef_unspecified_cut
754 chicken_heart&chicken_gizzard
755 sashimi_grade_tuna
756 tuna_fillet
757 beef_shank
758 chicken_leg&chicken_thigh&chicken_wing
759 skinless_chicken_breast_fillet
760 chicken
761 clam&water
762 fish_fillet
763 daikon
764 cooked_linguine_noodles
765 miki_lucban_noodle|pancit_canton_noodle
766 pork_cutlet
767 pork|pork_belly
768 prawn
769 luglug_rice_noodle
770 half_shell_scallop
771 shelled_shrimp_with_tail
772 upo
773 lemon_lime_soda
774 bone_in_center_cut_pork_loin_rib_chop
775 garlic
776 water
777 taro_root
778 green_finger_chili
779 calamansi_juice
780 chicken_wing|chicken_breast|chicken_leg
781 bottled_tuyo|fried_tuyo
782 suahe_shrimp
783 hotdog|wiener
784 shelled_headless_prawn
785 sweet_gherkin_pickle
786 yard_long_bean
787 chicken_leg_quarter
788 lemongrass
789 muscovado_sugar|coconut_sugar
790 calamansi
791 napa_cabbage
792 garlic
793 chicken
794 unripe_tamarind
795 ripe_guava
796 chicken
797 bacon
798 chicken_stock|(chicken_bouillon_cube&water)
799 dried_shiitake_mushroom&water
800 half_shell_oyster
801 bihon_noodle
802 extra_firm_tofu
803 calamansi
804 yard_long_bean
805 thai_chili|siling_labuyo
806 thai_chili
807 thai_chili
808 ground_pepper_unspecified_type
809 sweet_basil_leaves
810 annatto_oil
811 sugar
812 $bamboo_skewer
813 $banana_leaf_wrapper
814 siling_labuyo
815 bottled_milkfish_in_olive_oil
816 calamansi
817 calamansi_juice
818 canola_oil|vegetable_oil
819 carabao_meat|beef_bottom_round
820 siling_labuyo_flake
821 siling_labuyo
822 tamarind_powder|kamias|calamansi_juice|lemon_juice
823 cilantro_leaves
824 !non_ingredient
825 coconut_cream
826 coconut_sap_vinegar
827 cooking_oil|vegetable_oil|corn_oil|canola_oil|peanut_oil
828 crispy_fried_garlic_bits
829 !source_issue
830 calamansi
831 spring_onion
832 long_green_chili
833 siling_pangsigang
834 !non_ingredient
835 !non_ingredient
836 fried_garlic
837 crispy_fried_garlic
838 garlic
839 garlic_flake
840 green_leaf_lettuce
841 green_onion
842 cooked_white_rice
843 shrimp_juice
844 lemon_juice
845 lime_juice|calamansi_juice
846 !source_issue
847 celery_leaves
848 $kitchen_twine|$pandan_leaf_tie
849 avocado
850 lemon
851 lettuce
852 margarine
853 $metal_skewer|$bamboo_skewer
854 cooked_mini_meatball
855 nonstick_cooking_spray|cooking_oil
856 nori
857 cooking_oil
858 cooking_oil
859 olive_oil
860 grape&mint_leaves
861 !source_issue
862 !source_issue
863 paella_seasoning
864 parsley
865 !non_ingredient
866 pig_parts_unspecified
867 pork_ear
868 red_finger_chili
869 red_bell_pepper
870 salt
871 salt&black_pepper
872 salt&ground_pepper_unspecified_type
873 salt
874 sea_salt
875 vegetable_oil
876 quick_melt_cheese
877 siling_labuyo
878 sinigang_mix
879 sliced_bread|pandesal
880 spinach|kangkong
881 steamed_white_rice
882 !source_issue
883 togarashi
884 vegetable_oil
885 vegetable_oil
886 vegetable_oil
887 vegetable_oil
888 cilantro
889 water|egg
890 water|egg_wash
891 water
892 white_vinegar
''')

# These are decisions made from the supplied line and its actual recipe context,
# not a re-run of the failed shared parser.
M.update({8: 'boiled_beef_tripe&salt', 211: 'ripe_guava&semi_ripe_guava',
          298: '!source_issue', 323: 'reserved_seafood_boil_broth',
          388: 'toasted_hoti', 428: 'tapioca_flour', 567: 'parsley',
          690: 'grilled_chicken', 719: 'sweet_gherkin_pickle', 847: 'kinchay'})
M.update({85:'fresh_shrimp|dried_shrimp',418:'fresh_kamias|frozen_kamias',
          440:'soaked_dried_chili',682:'soaked_white_kidney_bean'})
M.update({164:'lechon_manok',290:'whole_cornish_game_hen',
          498:'uncooked_seasoned_yellow_rice',813:'$banana_leaf_serving_sheet'})
M.update({160:'liver_unspecified_animal',
          293:'chicken_wing|chicken_thigh|chicken',
          336:'chicken_breast_fillet|chicken',
          650:'chicken_wing_drumettes_and_flats|chicken'})
M.update({420:'steamed_shelled_headless_shrimp',
          521:'dried_fish|dried_labahita_fillet'})
# Preserve the explicit main food name without globally treating a conflicting
# translation as its synonym. Root review confirmed this annotation policy.
GLOSSES = {
288: ('maya_maya', 'grouper'),
298: ('chinese_cabbage', 'repolyo'),
534: ('thai_chili', 'siling labuyo'),
586: ('thai_chili', 'siling labuyo'),
588: ('thai_chili', 'siling pansigang'),
599: ('thai_chili', 'siling labuyo'),
668: ('thai_chili', 'siling pangsigang'),
726: ('kinchay', 'parsley'),
733: ('thai_chili', 'siling labuyo'),
829: ('crushed_piquin_pepper', 'siling labuyo'),
846: ('lemon_juice', 'katas ng dayap'),
861: ('thai_chili', 'siling labuyo'),
862: ('lemon', 'hiwa ng dayap'),
882: ('thai_chili', 'siling labuyo'),
}
for index, (identity, gloss) in GLOSSES.items(): M[index] = identity
NOTES.update({
0: 'Source explicitly identifies smoked milkfish / tinapang bangus; smoked state is retained, not raw fish.',
1: 'Pack weight does not change the named linguine. The line explicitly requires noodles already cooked according to their package.',
2: 'Malformed -i-inch quantity is not repaired; the food identity ginger is explicit.',
3: 'The explicit pig leg identity is retained; weight and serving cuts remain in the original line.',
8: 'Ox tripe is explicitly washed with salt and boiled; the boiled state and named washing salt are retained.',
9: 'Prepared pork adobo with sauce removed; this is not a raw pork identity or an added sauce requirement.',
10: 'The source joins chicken thighs AND drumsticks, so both named cuts are retained.',
11: 'The ingredient is prepared shrimp fried rice. The click-for-recipe wording is a link prompt, not an additional food.',
13: 'Beef seasoning powder OR one beef cube are explicit alternatives; powder is not a meat-cube identity.',
14: 'Raw shelled peanuts are explicit; skin-on or skin-off are both permitted by the same line.',
15: 'Both pig heart and lung are pre-boiled; the line explicitly names water, white vinegar and ginger for that preparation.',
19: '7-Up or Sprite identifies lemon-lime clear soda; neither brand becomes a separate required ingredient.',
22: 'Coconut milk powder is explicitly dissolved in water; both powder and water are required, rather than assuming canned milk.',
25: 'Seasoning powder and unspecified-flavor broth cube are explicit alternatives; no animal flavor is invented.',
28: 'Canned sardines in oil are explicitly drained with their own oil reserved; this does not assert a new, separately purchased oil.',
30: 'Bok choy OR pechay is preserved as the written choice, without asserting universal equivalence.',
31: 'Fresh spinach OR moringa/malunggay leaves is an explicit alternative, not a requirement for both greens.',
41: 'The food is explicitly misua and the method says add misua. The parenthetical fine-rice-noodles gloss is not used to equate misua with rice noodles.',
49: 'Canned water chestnuts are explicit in the English head and measure; kastanyas is an imprecise gloss, not an added chestnut requirement.',
54: 'The misspelled cip is a quantity token; sitaw identifies the beans.',
60: 'Calamansi juice OR a blend of lime juice AND orange juice: the substitute blend is kept together as a conjunction.',
67: 'Fresh breadcrumbs made from pandesal are a prepared ingredient, not an extra requirement for both crumbs and a loaf.',
68: 'The source explicitly specifies sauteed shiitake seasoned with salt and pepper; pepper variety is not stated.',
70: 'Sitaw specifies yard-long beans; generic green beans is not used as a universal identity alias for every bean variety.',
71: 'The method explicitly says add bell peppers with the sauces, corroborating green bell pepper; the siling pangsigang translation is inconsistent and is not adopted as an alias.',
77: 'Source permits greaseless, unsalted peanuts; unsalted is retained without inventing a roasting step.',
79: 'This is pineapple juice already reserved from the canned pineapple, not an arbitrary replacement fruit juice.',
80: 'Grated potatoes are kept in water, both named materials are preserved.',
81: 'Lengua Estofado boils beef tongue in seasoned water and explicitly reserves one cup of that broth; it is reserved beef broth, not unspecified new stock.',
85: 'The source explicitly allows fresh OR dried small shrimp; dried shrimp is not silently equated with fresh shrimp.',
97: 'Egg is beaten and explicitly seasoned with salt and unspecified pepper; all three foods are retained.',
99: 'The curry method repeatedly names bell peppers and distinguishes optional Thai chilies. Green bell pepper is supported; incorrect pangsigang gloss is not a new alias.',
109: 'The method explicitly seasons and grills chuck steak. This resolves the cut as beef chuck despite the inaccurate litid translation.',
114: 'Boneless beef ribs OR beef brisket are explicit cut alternatives.',
115: 'The same method explicitly says marinate chopped beef sirloin, supporting sirloin rather than turning the inaccurate litid gloss into tendon.',
117: 'Chicken legs / thighs denotes permitted cut choices; neither is generalized to chicken breast.',
129: 'The source directs separation of pork fat from meat, not discarding fat; both identities are retained.',
140: 'Country-style boneless pork ribs OR pork belly: the allowed cut alternatives remain distinct.',
142: 'The line calls for shelled shrimp and explicitly reserves heads and shells; the retained parts are not discarded from the requirements.',
143: 'Squid ink is explicitly set aside along with the sliced squid; it is retained as a named food part.',
149: 'Chicken breast is already pre-boiled and shredded; cooked state is preserved.',
160: 'The ingredient head is liver with animal unspecified. Pig or cow liver are described as best, so those are preferences rather than mandatory species restrictions.',
171: 'Ampalaya is explicitly washed in sea salt and water; these named handling materials remain visible.',
172: 'Bell pepper is explicit and the method says dice and saute bell peppers; the generic paminta gloss is not promoted to peppercorn.',
187: 'Dried banana blossom is washed and soaked in water; dried form and named water are retained.',
191: 'Wood-ear mushroom is explicitly soaked in water until softened; the water is named rather than assumed.',
193: 'Shared head noodles applies to cornstarch OR rice-stick options; the expression does not recommend loose cornstarch as noodles.',
198: 'Counted beef cube OR pork cube OR beef powder are explicit seasoning alternatives; species and form are not erased.',
207: 'The method explicitly adds red and green bell peppers; the contradictory pangsigang parenthetical is not treated as a substitution.',
211: 'The source asks for ripe AND semi-ripe guavas. Both ripeness forms are retained, with original amount unchanged.',
238: 'Red bell pepper is supported by both the ingredient head and the method; pamintang pula is not parsed as a second spice.',
239: 'Red bell pepper is retained from the specific English head; the recipe instruction context is inspected for bell pepper use, and the pangsigang gloss is flagged as unreliable wording.',
248: 'The method explicitly lists chili flakes separately from black pepper; the imprecise paminta gloss does not erase the chili identity.',
250: 'The head explicitly says fish sauce; paris is a misspelling in the gloss, not a new food.',
251: 'Garlic paste is explicitly defined as garlic pounded with a little salt, so both named ingredients are retained.',
264: 'Annatto powder OR annatto seeds steeped in water: the two-food seed preparation stays grouped as an alternative.',
273: 'This is breadcrumbs prepared from sliced bread; the food-processor and hand-tearing directions do not become ingredients.',
288: 'The source simultaneously says maya-maya and grouper, which are different fish identities. Both supplied variants say only fish in the method; neither disambiguates the species. No false any-of substitution is invented.',
293: 'Wings OR thighs/other chicken parts are allowed. Retain the named cuts plus the broad chicken option; other parts does not mean a required mixture of cuts.',
298: 'The line says Chinese cabbage but gives repolyo as its translation. The method says cabbage without identifying a variety. Napa cabbage versus ordinary cabbage cannot be established from this supplied recipe.',
300: 'Annatto seeds explicitly diluted in water require both seeds and water; this is not annatto oil.',
301: 'Banana ketchup OR tomato ketchup is explicit; the suggested brand is not a separate ingredient.',
307: 'Daing is explicitly salt-dried fish already fried; fried dried form is retained.',
308: 'Daing is explicitly already fried and has bones removed; no raw-fish equivalence is asserted.',
310: 'The source specifies sitaw, retaining yard-long bean identity rather than treating all green beans as equivalent.',
321: 'Use adobo cut describes a pork cut, not explicitly cooked adobo; the source word shredded does not justify inventing cooked state.',
323: 'The seafood-boil method reserves the water used to cook crab, shrimp, sausage, potatoes, corn and aromatics; record its distinct prepared seafood-boil broth identity, not beef or chicken broth.',
326: 'Tinapang galunggong identifies smoked round scad, with skin and bones removed.',
328: 'Stock is explicitly derived from shrimp heads, retaining shrimp-stock identity rather than an arbitrary meat stock.',
334: 'White OR yellow miso are explicit permitted varieties, not a requirement for both.',
338: 'Kalitiran is the named beef cut (shoulder clod); it is not flattened into generic beef or assumed sirloin.',
344: 'Galunggong is the explicit named fish; round scad identity is retained and the loose mackerel gloss is not used as a universal synonym.',
351: 'Peeling does not remove the explicitly retained head and tail; the requirement keeps shelled shrimp with head and tail.',
355: 'The line permits crab legs/claw and specifies alimango/mud crab; preserve the part choice and crab type.',
366: 'The red onion is explicitly left in salted cold water; onion, water and salt are all named.',
370: 'Pepper variety is not stated; no automatic black-pepper assumption is made.',
376: 'Ground bay leaf OR a finely chopped whole leaf is explicit; both forms remain alternatives.',
379: 'Calamansi juice is explicit. The see-alternatives-below instruction contains no named alternative in this line, so none is invented.',
388: 'Hoti is explicitly named as an edible topping, dry-toasted then mixed with fried sotanghon in the actual method. Its named toasted-product identity is retained without guessing its composition.',
408: 'The Tagalog instruction gamitin ang petsong nilaga explicitly means use boiled chicken breast; the state and breast cut are retained.',
418: 'Fresh OR frozen kamias is explicit; frozen state is represented as the written alternative.',
424: 'Sili tops names the edible chili leaves/tips rather than chili fruits.',
428: 'The method specifically says put tapioca flour on a plate and coat the chicken in it. Tapioca flour is retained; the cassava-flour gloss is not an asserted universal equivalence.',
435: 'Drumsticks explicitly specifies chicken leg meat; the paa gloss is not used to convert these to chicken feet.',
437: 'Soup reserved from bulalo is a prepared bulalo broth dependency, not an unspecified carton of stock.',
442: 'Whole tamarind OR a measured package of tamarind-base powder are explicit alternatives.',
447: 'Prepared beef stock OR beef bouillon cube diluted in water: keep the cube AND water branch grouped.',
455: 'Pechay is explicitly named; Chinese cabbage is a broad gloss and no unsupported Napa subtype is introduced.',
476: 'The line only specifies peeled grated papaya; it does not explicitly establish green or ripe state, so papaya remains unspecified.',
483: 'The line explicitly calls for food coloring and flavoring and names langka flavor; retain coloring plus jackfruit flavoring rather than whole jackfruit.',
498: 'The named food is seasoned yellow rice/arroz amarillo. The method first soaks the rice, then cooks it until done, establishing that this requirement is uncooked seasoned rice, not already cooked rice. No spice composition is invented.',
514: 'Dried taro leaves are explicit. The accompanying safety prose is retained in raw text and is not treated as additional food or independently validated advice.',
517: 'Sole fillet OR any white-fleshed fish fillet is explicitly permitted; the broader fish alternative is not invented.',
520: 'The coconut ingredient explicitly includes both juice and meat; both named coconut components are required.',
521: 'The head specifies dried fish and gives daing OR labahita fillet as its alternatives. The method adds dried fish, so dried state applies to both branches.',
528: 'Long red chili OR Thai chili is an explicit choice. The labuyo gloss attached to Thai chili is not used as a universal synonym.',
534: 'Thai chili and siling labuyo are conflated without an explicit alternative or disambiguating context; varietal identity needs source clarification.',
536: 'Bottom round OR top round are explicit beef cuts, retained as choices rather than an asserted equivalence.',
537: 'The source permits thigh OR leg meat, both explicitly boneless and skinless.',
539: 'The source permits chicken thigh OR breast meat, both explicitly boneless and skinless.',
544: 'Pork face/snout and ears are jointly specified by maskara at tainga ng baboy; both pork face and pork ear are retained.',
556: 'Sili leaves is corroborated by the method adding sili leaves to the laing sauce. Small is an amount qualifier, not a different ingredient.',
564: 'The only unnamed ingredient is 2 tablespoons. The same recipe starts by heating oil, and its ingredient list contains no other oil entry. Recover cooking oil from this specific context; the quantity remains untouched.',
567: 'The seafood-boil serving step explicitly says sprinkle chopped parsley. Retain parsley, not the inaccurate kintsay gloss or an invented both-herbs requirement.',
569: 'Tunawin sa 3 kutsara ng tubig directs dissolving cornstarch in water; both are explicit.',
583: 'Annatto powder is explicitly mixed with water; both named ingredients remain required.',
586: 'Thai chili versus siling labuyo is an inconsistent varietal gloss and the supplied recipe does not disambiguate it; do not invent an authorized alternative.',
588: 'Thai chili and siling pangsigang name different chili varieties in the same line. The method only says chilies and supplies no choice, so source clarification is required.',
599: 'Thai chili and siling labuyo are conflated without an explicit or alternative; the supplied recipe repeats rather than resolves that ambiguity.',
606: 'The method explicitly permits speck OR etag, retaining the two distinct cured/smoked meat products.',
610: 'The line explicitly says Baguio beans; long is a shape description, not a reason to replace them with sitaw.',
614: 'Unripe tamarind is explicitly boiled in water; unripe state and the named water remain visible.',
616: 'Shrimp are shelled and deveined while heads and tails remain on; keep the retained parts in the named form.',
617: 'Firm tofu/tokwa is explicit. The manual database-insertion comment is editorial metadata, not a food identity.',
629: 'Jalapeo is a damaged jalapeno spelling; the head uniquely identifies that pepper, while siling verde is a generic green-chili gloss.',
648: 'Chicken thigh meat is explicitly boneless and skinless; neither constraint is discarded.',
650: 'The recipe permits replacing chicken wings with other chicken parts. Preserve the wing drumettes/flats form and a broad chicken alternative, without inventing a mixed-cut requirement.',
660: 'The source explicitly offers bagoong alamang OR guinamos; retain the named fermented products without guessing the species composition of guinamos.',
668: 'Thai chili and siling pangsigang conflict; the supplied method does not establish which variety is intended.',
682: 'White kidney beans/cannellini is the named variety and is already soaked overnight. Preserve the soaked state without inventing a separately quantified soaking liquid.',
688: 'The actual method explicitly combines vinegar and calamansi juice, resolving the loose calamansi-lemons wording as calamansi juice.',
690: 'The cooked chicken is further specified as inihaw na manok (grilled chicken), so the grilled preparation state is retained.',
694: 'Hugas bigas identifies rice-washing water, not plain water or uncooked rice itself.',
700: 'Squid are explicitly stripped of head, tentacles and skin; the remaining mantle form is retained.',
709: 'The source explicitly requires breast pieces AND two legs, not an either-or choice.',
719: 'Sweet gherkin pickles is the specific named ingredient and the method fills the roll with pickle strips. Atchara is an inaccurate gloss here; no equivalence with pickled papaya is asserted.',
726: 'The ingredient conflates kinchay with parsley while the method only says mix the ingredients. The supplied recipe does not disambiguate the different herbs.',
728: 'Cornstarch is explicitly dissolved in pork broth, preserving both named requirements rather than assuming plain water.',
731: 'The source explicitly says use sukang Iloko, retaining the named regional vinegar form.',
733: 'Thai chili and siling labuyo are conflated without a stated choice; no source evidence disambiguates their varietal identity.',
743: 'Pork shoulder is explicit; chasm is a corrupted gloss rather than another food.',
745: 'Chicken wings explicitly have tips trimmed and reserved. Both wing and retained tip material are represented.',
753: 'Beef brisket OR any cheap beef cut is explicitly allowed; the broad beef-cut option is source wording, not a model-created substitution.',
755: 'The line explicitly requires sashimi-grade tuna; no claim is made that arbitrary tuna satisfies this preparation constraint.',
756: 'Tuna fillet is the head. Sashimi-grade or IQF is a stated preference, not a strict conjunction; the preference remains in original text for later recipe review.',
758: 'The line lists chicken legs, thighs AND wings; each named cut is retained.',
762: 'The source explicitly allows any fish fillet and gives tilapia as an example; fish-fillet identity preserves that breadth without restricting to tilapia.',
774: 'Bone-in center-cut pork loin rib chops is a specific named cut; bone and cut constraints are retained.',
775: 'Garlic is the actual ingredient, corroborated by the sauteing step. The sample database-update note is editorial metadata.',
781: 'Bottled tuyo OR fried tuyo is explicit; those prepared forms remain alternatives.',
795: 'Ripe guavas are explicit. A replacement-character separator does not erase the identity; mixed-ripeness preference remains in the original line.',
798: 'Prepared chicken stock OR chicken bouillon cubes diluted in water; cube AND water remain grouped within that option.',
799: 'The head says dried fresh shiitake, but rehydration in hot water specifically supports dried shiitake. Preserve the dried form and named water, noting the contradictory fresh adjective.',
805: 'Thai chili OR siling labuyo is explicit, so represent permitted alternatives rather than making a synonym rule.',
808: 'An unreadable amount does not obscure the named ground pepper; pepper variety remains unspecified and quantity is not guessed.',
812: 'Bamboo sticks are explicitly for spearing: equipment, not food.',
813: 'The banana leaf is cleaned and cut into serving sheets. The habhab method arranges noodles on top of each leaf; it is a serving material, not an edible ingredient or a required wrapping operation.',
819: 'Carabao meat OR beef bottom round is explicitly allowed; retain both named meat choices.',
822: 'Choice of souring agent lists tamarind powder, bilimbi, calamansi juice OR lemon juice; these are options, not four required foods.',
824: 'The preceding ingredient is a whole head of garlic. The method instructs halving its cloves. This detached preparation fragment is not clove spice or an extra garlic quantity.',
827: 'Cooking oil is the general requirement; vegetable, corn, canola and peanut oils are explicitly acceptable examples, retained as choices rather than all required.',
829: 'Piquin peppers and siling labuyo are different named varieties. The Mexican menudo method gives no evidence that makes them identical or establishes a substitution.',
834: 'This is a detached preparation instruction for the preceding ripe mangoes; the method explicitly scoops mango flesh into a blender. It adds no separate ingredient.',
835: 'For the vegetables is a section heading, not a food item.',
839: 'Garlic flakes are explicitly named for garnish; the cooking method also sautes separate garlic. Preserve the flake form instead of assuming raw chopped cloves.',
843: 'The source explicitly calls for juice extracted from shrimp heads; retain shrimp-juice identity, not whole shrimp or generic stock.',
846: 'The source says lemon juice and repeats dayap/lime as its translation in the method. It does not state an either-or choice; the citrus species conflict is retained for source correction.',
847: 'Kinchay is the explicit garnish identity. Its source does not name parsley, so no cross-herb synonym is invented.',
848: 'Kitchen twine OR pandan leaves are expressly used for tying; they are cooking aids here, not required edible foods.',
853: 'Metal OR bamboo skewers are equipment; the soaking instruction does not turn them into a food.',
861: 'Thai chilies and siling labuyo are conflated in the optional ingredient without disambiguation; optionality does not justify a false variety alias.',
862: 'Lemon slices and dayap/lime are conflated in both ingredient and method. No explicit citrus alternative is given, so source clarification remains needed.',
865: 'This detached peeling/slicing direction belongs to the preceding fresh ginger, as the tea method confirms. It is not an extra ingredient quantity.',
869: 'The method explicitly sautes red bell peppers and garnishes with red pepper slices, supporting red bell pepper rather than ground red spice.',
879: 'Sliced bread OR pan de sal is explicitly permitted for serving.',
880: 'Spinach OR kangkong/water spinach is an explicit choice; they are not required together.',
882: 'Thai chili and siling labuyo are conflated in the source and its serving instruction; the same mistranslation is not independent disambiguating evidence.',
889: 'Water OR egg for egg wash is explicitly stated; egg is not an additional mandatory ingredient when water is chosen.',
890: 'Water OR prepared egg wash for sealing is explicit; the composition of egg wash is not invented.',
})

def expression(text):
    def split_top(value, delim):
        pieces, start, depth = [], 0, 0
        for pos, char in enumerate(value):
            depth += (char == '(') - (char == ')')
            if char == delim and depth == 0:
                pieces.append(value[start:pos]); start = pos + 1
        pieces.append(value[start:])
        return pieces
    if text.startswith('(') and text.endswith(')'):
        depth, wraps = 0, True
        for p,c in enumerate(text):
            depth += (c == '(') - (c == ')')
            if depth == 0 and p < len(text)-1: wraps = False
        if wraps: return expression(text[1:-1])
    for sep, key in [('|', 'any_of'), ('&', 'all_of')]:
        parts = split_top(text, sep)
        if len(parts)>1: return {key: [expression(p) for p in parts]}
    if text.startswith('$'): return {'equipment_id': text[1:]}
    assert re.fullmatch('[a-z][a-z0-9_]*', text), text
    return {'ingredient_id': text}

assert set(M) == set(range(len(rows))), set(range(len(rows))) - set(M)
REUSE = {
    'ampalaya':'bitter_melon', 'baguio_bean':'green_bean',
    'yard_long_bean':'sitaw', 'blanched_yard_long_bean':'blanched_sitaw',
    'moringa_leaves':'malunggay_leaf', 'green_onion':'spring_onion',
    'green_onion_leaves':'spring_onion_leaf', 'cilantro_leaves':'cilantro_leaf',
    'pandan_leaves':'pandan_leaf', 'taro_root':'taro', 'taro_leaves':'taro_leaf',
    'dried_taro_leaves':'dried_taro_leaf', 'kalabasa':'squash',
    'patola':'sponge_gourd', 'upo':'bottle_gourd', 'singkamas':'jicama',
    'breadcrumb':'bread_crumbs', 'pepper_unspecified_type':'pepper_unspecified',
    'ground_pepper_unspecified_type':'ground_pepper_unspecified',
    'round_scad':'galunggong', 'smoked_round_scad':'smoked_galunggong',
    'fried_round_scad':'fried_galunggong', 'salted_round_scad':'salted_galunggong',
    'corn_on_cob':'corn_on_the_cob', 'beef_shoulder_clod':'beef_kalitiran',
    'red_chili_flake':'red_chili_pepper_flakes',
    'chicken_breast_fillet':'boneless_chicken_breast',
}
for index, value in list(M.items()):
    M[index] = re.sub(r'[a-z][a-z0-9_]*', lambda m: REUSE.get(m.group(),m.group()), value)
decisions = []
for index, row in enumerate(rows):
    expr = M[index]
    status = 'resolved'
    requirement = None
    if expr.startswith('!'): status = expr[1:]
    elif '$' in expr and all('$' in token for token in re.split(r'[|&]',expr)):
        status = 'non_ingredient'
    else: requirement = expression(expr)
    if index in NOTES: basis = NOTES[index]
    else:
        names = expr.replace('&', ' AND ').replace('|', ' OR ').replace('_',' ')
        basis = f'The source explicitly names {names}; quantity, size and cutting directions remain in the original text and do not create another ingredient. Named preparation/state constraints are retained in the identity.'
    if index in GLOSSES:
        identity, gloss = GLOSSES[index]
        basis = (f'Retain the explicitly named main ingredient {identity.replace("_", " ")}. '
                 f'The source gloss "{gloss}" is not a universal identity alias or an authorized substitution. '
                 'Its terminology discrepancy remains flagged for recipe/source review; quantities and original wording are preserved.')
    result = dict(ingredient_line=row['ingredient_line'], status=status,
                  requirement=requirement, basis=basis,
                  annotation_type='ai_semantic_annotation',
                  reviewer='Codex parallel semantic annotation; not independent human review')
    if status == 'non_ingredient' and '$' in expr:
        result['equipment_requirement'] = expression(expr)
    if index in GLOSSES:
        result['source_gloss'] = GLOSSES[index][1]
        result['terminology_review_required'] = True
    if index == 160:
        result['preferred_ingredients'] = ['pork_liver', 'beef_liver']
        result['preference_is_not_requirement'] = True
    decisions.append(result)
(ROOT/'partition_03.decisions.json').write_text(json.dumps(decisions,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
from collections import Counter
print(Counter(r['status'] for r in decisions))
print('Occurrences:', sum(r['occurrences'] for r in rows))
print('Source issues:', [(i,rows[i]['ingredient_line']) for i,v in M.items() if v == '!source_issue'])
