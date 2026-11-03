"""Explicit semantic annotation decisions for frozen partition 01; never trains a model."""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
rows = json.loads((ROOT / 'partition_01.json').read_text(encoding='utf-8'))
vocabulary = json.loads((ROOT / 'canonical_vocabulary.json').read_text(encoding='utf-8'))
baseline = json.loads((ROOT / 'baseline_requirements.json').read_text(encoding='utf-8'))
known = set(vocabulary.values())

# These are manual semantic readings, indexed against the immutable assigned input.
# Quantity, ordinary knife cuts, serving suggestions and optionality stay in source text;
# meaningful food forms, prepared subrecipes, meat cuts and alternatives are retained here.
# '+' means explicitly combined ingredients; '|' means an explicit choice, never conjunction.
READINGS = '''
0 cheddar_cheese
1 grouper
2 beef_flavored_instant_ramen
3 ginger
4 siling_labuyo
5 leftover_roast_chicken
6 pork_giniling_kaldereta
7 vinegar
8 ginger
9 meatball
10 pork_shoulder
11 milkfish
12 ground_toasted_rice
13 oyster_sauce
14 peppercorn
15 sweet_and_sour_sauce
16 saba_banana
17 hot_spicy_canned_tuna
18 knorr_sinigang_sa_sampaloc_mix_original
19 canned_button_mushroom
20 yellow_curry_powder|curry_seasoning_mix
21 orange_soda|lemon_lime_soda
22 tamarind_soup_base_mix
23 coconut_milk_powder+water
24 daikon_radish
25 tuna_belly
26 whole_wheat_fusilli
27 red_bell_pepper
28 black_olive
29 broccoli_crown
30 bok_choy
31 bok_choy
32 spinach|malunggay_leaves
33 spring_onion
34 kangkong_leaves
35 kangkong
36 malunggay_leaves
37 saluyot_leaf
38 string_bean
39 kangkong
40 winged_bean
41 spring_onion
42 blanched_native_pechay
43 sitaw
44 chunky_corned_beef
45 chunky_corned_beef
46 salted_black_bean
47 chunky_corned_beef
48 canned_diced_tomato
49 canned_green_jackfruit
50 evaporated_milk
51 lemon_lime_soda
52 carrot
53 chicken_bouillon_cube+water
54 siling_labuyo
55 mature_coconut_meat
56 pork_bouillon_cube
57 all_purpose_flour+salt+pepper_unspecified+sinigang_sa_kamias_powder_mix
58 ampalaya_leaves
59 bean_sprout
60 bread_crumbs+sinigang_sa_kamias_powder_mix
61 carrot
62 napa_cabbage
63 seven_up|sprite
64 cornstarch
65 crushed_pineapple
66 dried_kamias
67 fat_free_italian_dressing
68 jackfruit
69 shrimp|prawn|mixed_seafood_with_fish_ball_and_crabstick
70 glutinous_rice_flour|galapong
71 sitaw
72 green_mango_puree
73 himbabao
74 medium_grain_rice
75 malunggay_leaves
76 blanched_napa_cabbage
77 vinegar
78 pico_de_gallo
79 pineapple_chunk
80 canned_pineapple_juice
81 premium_soy_sauce
82 reserved_beef_tongue_broth
83 sarangani_bay_bangus_tocino
84 dinorado_rice
85 chorizo
86 cooked_squid
87 beef_stock|pork_stock|chicken_stock
88 string_bean|green_bean
89 smoked_fish_flakes
90 ground_unsalted_peanut
91 vinegar
92 water
93 white_miso
94 winged_bean
95 sitaw
96 young_coconut_meat
97 mussel|littleneck_clam
98 egg_white
99 green_bell_pepper
101 green_bell_pepper
103 siling_pangsigang
104 sweet_potato_top
105 broccoli
106 unpeeled_garlic
107 unpeeled_garlic
108 toasted_garlic
109 beef_brisket|beef_rib
110 goat_meat
111 mackerel
112 pork_loin|pork_belly|pork_shoulder
113 beef_brisket
114 beef_shank
115 beef_rib
116 blue_crab|mud_crab
117 chicken_breast
118 chicken_leg|chicken_thigh
119 chicken_adobo_cut
120 chicken_drumsticks
121 chicken_thigh_fillets
122 salted_hiwas|salted_sapsap|salted_bisugo|salted_galunggong
123 ham_hock
124 lamb_shoulder
125 boneless_pork_belly
126 headless_tailless_milkfish
127 pork_shoulder|pork_belly
128 pork_belly
129 pork_belly
130 pork_bone_with_meat
131 pork
132 boneless_pork_belly
133 pork_shoulder
134 pork_belly
135 pork_shoulder
136 salmon_belly|salmon_head
137 squid_with_ink_sac
138 tilapia_fillet
139 whole_chicken
140 chicken_wing
141 green_mussel
142 pork_ham
143 shell_on_shrimp
144 tuna_jaw
145 milkfish
147 canned_pineapple_slice
148 carrot
149 carrot
150 eggplant
151 ripe_mango
152 onion
153 patola
154 pompano
155 potato
156 seedless_watermelon
157 tilapia_steak
158 whole_tilapia|whole_grouper|whole_red_snapper
159 cooked_pork_adobo_with_sauce
160 honeycomb_tripe
161 pig_large_intestine
162 shell_head_on_shrimp+salt
163 beef_sirloin|pork_sirloin
164 shell_on_shrimp
165 lechon
166 green_bean
167 pig_large_intestine
168 clam
169 lemon_juice
170 water
171 maggi_chicken_cube
172 napa_cabbage
173 bell_pepper
174 carrot
175 green_papaya
176 native_red_bell_pepper
177 onion
178 red_bell_pepper
179 red_bell_pepper
180 serrano_pepper
181 bottle_gourd
182 tomato
183 white_onion
184 yellow_onion
185 yellow_sweet_potato
186 seedless_navel_orange
187 italian_style_tomato_sauce
188 palabok_noodle
189 soaked_rice_noodle
190 spaghetti
191 filipino_style_tomato_sauce
192 baby_corn
193 cornstarch_stick|rice_noodle
194 tamarind_soup_base_mix
195 maggi_magic_sarap
196 siling_pangsigang
197 banana_leaf
198 beef_bouillon_cube|pork_bouillon_cube
199 siling_labuyo
200 boneless_chicken_breast
201 chorizo_de_bilbao
202 ginger
203 siling_pangsigang
204 knorr_beef_cube
205 lemongrass_white_part
206 scaled_on_gutted_milkfish
207 pork_heart
208 siling_labuyo
209 siling_labuyo
210 pig_leg
211 pork_leg
212 ripe_guava+semi_ripe_guava
213 chicken_skin+chicken_fat
214 fresh_button_mushroom
215 ground_beef
216 shell_head_on_shrimp
217 fish_fillet
218 shell_on_shrimp
219 head_on_shrimp
220 first_press_coconut_milk
221 prepared_stuffed_chicken_breast
222 red_bell_pepper
225 red_chili
226 blanched_chayote
227 crispy_fried_jeprox
228 teriyaki_sauce
229 tenderized_pork_belly
230 lemon
231 bottle_gourd
232 squash
233 daikon_radish
234 green_bell_pepper
235 cauliflower
236 onion
237 patola
238 red_bell_pepper+green_bell_pepper
239 red_bell_pepper
240 red_bell_pepper
241 rosemary
242 white_onion
243 lemongrass_bottom_part
244 cinnamon_stick
245 oyster_sauce
246 aligue_paste
247 oyster_sauce
248 annatto_seed+pork_broth
249 chive|spring_onion
250 cooking_oil
251 basil_leaf
252 ginger
253 ginger
254 ginger
255 korean_hot_pepper_paste
256 miso_paste
257 siling_labuyo|thai_chili
258 semi_sweet_chocolate
259 soy_sauce
260 tamarind_soup_base_mix
261 tomato_paste
262 sauteed_shrimp_paste
263 sweet_soy_sauce|dark_soy_sauce
264 crushed_red_pepper|red_chili
266 shrimp_bouillon
267 siling_pangsigang
268 gochugaru
269 monosodium_glutamate
270 red_pepper_flake
271 salt
272 powdered_tamarind|calamansi_juice
273 ginger
274 chicken
275 steamed_taiwan_pechay|blanched_taiwan_pechay
276 black_pepper
277 white_onion
278 white_radish
279 bone_in_beef_shank
280 dressed_whole_chicken
281 whole_chicken
282 whole_chicken
283 whole_chicken
284 whole_duck
285 garlic
286 garlic
287 garlic
288 garlic
289 whole_native_chicken
290 red_onion
291 star_anise
292 zucchini
293 white_onion
294 pork_cheek+pork_ear+pork_snout
295 powdered_tamarind|fresh_tamarind_pulp
296 pork_leg
297 beef_neck_bone|beef_rib|oxtail|stewing_beef
298 beef_bouillon_cube|pork_bouillon_cube
299 seven_up|sprite
300 all_purpose_flour
301 annatto_seed+water
302 banana_ketchup|tomato_ketchup
303 bottled_tamarind_pulp|sinigang_sa_sampaloc_mix
304 canola_oil
305 kinchay
306 coconut_cream
307 chicharon
308 fried_firm_tofu
309 pineapple_jam|mango_jam
310 cheddar_cheese
311 spring_onion|leek
312 all_purpose_flour
313 calamansi_juice|lemon_juice
314 liver_spread
315 liver_spread|liver_pate
316 glutinous_rice
317 mung_bean
318 old_bay_seasoning
319 papaya_atsara
320 peanut_paste
321 pork_liver
323 quick_melt_cheese
324 sake
325 smoked_fish_flakes
326 sitaw
327 butter|margarine
328 spring_onion
329 sugar
330 sweet_chili_sauce
331 tapuy|rice_wine
332 toasted_anchovy
333 unsalted_butter
334 water_chestnut
335 deep_fried_eggplant
336 green_bell_pepper
337 peeled_freshwater_shrimp+salt
338 yellowfin_tuna
339 lean_beef
340 beef_tripe
341 beef_sirloin
342 chicken_fillet
343 chicken
344 chicken_liver+chicken_heart
345 green_jackfruit
346 lean_ground_pork
347 boneless_country_style_pork_rib|pork_belly
348 boneless_country_style_pork_rib|pork_belly
349 pork_face
350 potato
351 green_tamarind
352 winged_bean
353 roasted_pork_belly
354 bottle_gourd
355 breakfast_beef_steak
356 lean_pork
357 ground_pork
358 dulong
359 lechon
360 lemon_juice
361 tamarind_soup_base_mix
362 squash+marble_potato
363 boneless_chicken_breast|boneless_chicken_thigh_meat
364 pork_heart
365 shell_on_shrimp
366 red_bell_pepper
367 napa_cabbage
368 ground_pepper_unspecified_type
369 cracked_black_peppercorn
370 ground_pepper_unspecified_type
371 red_pepper_flake
372 dried_fish
373 all_purpose_flour
374 ground_dried_shrimp
375 coconut_vinegar
376 dry_roasted_yellow_mung_bean
377 rock_salt|ground_salt
378 annatto_oil
379 bell_pepper
380 calamansi_juice|lemon_juice
381 canned_tausi
382 snow_pea
383 cilantro_leaf
384 cooking_oil
385 dark_soy_sauce
386 dried_shrimp_fry
387 bagoong_isda
388 spring_onion
389 iloko_vinegar|cane_vinegar
390 liver_spread|liver_pate
391 malunggay_seed
392 cooking_oil
393 sweet_creamy_peanut_butter
394 peanut_butter
395 ground_toasted_rice
396 shaoxing_cooking_wine
397 smoked_fish_flakes
398 fried_spice_paste
399 filipino_vinegar_unspecified_type
400 water|stock_unspecified_type
401 turmeric+water
402 beef_sirloin+soy_sauce+calamansi_juice
403 bell_pepper
404 chicken_gizzard
405 coconut_palm_heart+water
406 mussel+water
407 pork_cutlet
408 tripe_unspecified_animal+salt
409 cooked_peeled_shrimp
410 tulapho
411 sitaw
412 ground_pepper_unspecified_type
413 crushed_pepper_unspecified_type
414 squid_ink
415 misua
416 deep_fried_flour_tortilla
417 guava
418 ahi_tuna
421 celery
422 peeled_deveined_shrimp+shrimp_shell
423 lechon_kawali
424 peeled_shrimp_head_tail_on
425 boiled_mashed_tamarind
426 blanched_winged_bean
427 grated_coconut
428 mung_bean_sprout
429 water|chicken_broth
430 chicken
431 tamarind_soup_base_mix|fresh_tamarind
432 fish_sauce
433 white_glutinous_rice
434 sauteed_cherry_tomato
435 sitaw
436 fresh_kamias|frozen_kamias
437 large_sea_scallop
438 lumpia_wrapper
439 dried_pancit_canton_noodle
441 fresh_tamarind|tamarind_soup_base_mix
442 calamansi_juice
443 green_bean
444 green_bean
445 boneless_chicken_breast
446 peeled_prawn_head_tail_on
447 siling_labuyo
448 mild_cheddar_cheese|monterey_jack_cheese
449 thawed_frozen_green_jackfruit
450 tamarind
451 skinless_chicken_breast_fillet
452 garlic
453 firm_tofu
454 sweet_potato_tops_with_stalks
455 pechay
456 kangkong_stalk
457 kangkong
458 pork_and_beans
459 garlic
460 garlic
461 corn_on_the_cob
462 corn_on_the_cob
463 tofu
464 all_purpose_flour
465 kamias
466 cauliflower_floret
467 reserved_chicken_broth
468 napa_cabbage
469 coconut_palm_heart
470 crushed_ice
471 first_press_coconut_milk
472 frozen_seedless_grape
473 kangkong_stalk
474 lechon_sauce
475 kangkong+eggplant+okra+tomato
476 hickory_brown_sugar_barbecue_sauce
477 reserved_ham_poaching_liquid
478 reserved_chicken_broth
479 chicken_stock
480 squash
481 sweet_potato
482 boiling_water
483 young_coconut_meat
484 ube_food_flavoring+food_coloring_unspecified_color
485 red_food_coloring
486 sweet_corn_on_the_cob
487 egg
488 siling_pangsigang
489 spring_onion
490 green_leaf_lettuce
491 jalapeno_pepper
492 kaffir_lime_leaf
493 pork_belly
494 spring_onion_leaves
495 heat_softened_banana_leaf
496 sweet_potato
497 potato
498 ham_hock
499 tuna_jaw
500 chicken
501 grouper
502 shell_head_on_shrimp
503 pig_tail
504 wahoo_fillet
505 basil_leaf
506 lemon_juice
507 bitter_melon
508 carrot
509 onion
510 potato
511 red_onion
512 green_bell_pepper
513 bottle_gourd
514 onion
515 dried_taro_leaf
516 tomato_sauce
517 pandan_leaf
518 bitter_melon
519 chicken_thigh
520 skinless_chicken_breast_fillet
521 corn_on_the_cob
522 grilled_eggplant
523 whole_fish_unspecified_species
524 green_bell_pepper
525 hungarian_sausage
526 kaffir_lime_leaf
527 knorr_shrimp_cube
528 long_green_chili
529 siling_pangsigang
530 potato
531 red_bell_pepper|green_bell_pepper
532 saba_banana
533 long_chili
534 sweet_corn_on_the_cob
535 fish_fillet
536 garlic
537 chuck_roast|beef_top_round
538 heart_of_palm
539 boneless_beef_shank
540 carabao_meat|beef_bottom_round
541 goat_meat
542 shell_head_on_shrimp
543 pig_snout+pig_ear+pork_jowl
544 pork_butt
545 pork_hock
546 pork_sirloin
547 pork_spare_rib
548 salmon_belly|salmon_head
549 rice_wash
550 red_finger_chili
551 ripe_saba_banana
552 siling_pangsigang
554 bell_pepper
555 green_papaya
556 wood_ear_mushroom
557 firm_tofu
558 tomato
559 fried_firm_tofu
560 tofu
561 spring_onion
562 leek
563 spring_onion
564 fresh_alamang
565 bagoong_alamang
566 bottled_tamarind_paste
567 canola_oil
568 spring_onion
569 shaoxing_cooking_wine
570 dried_shrimp|meat_unspecified_animal
571 ginger
572 honey
573 liver_spread
574 neutral_cooking_oil
575 onion_powder
576 peanut_butter
577 peppercorn
578 toasted_rice_flour
579 salted_shrimp
580 sauteed_shrimp_paste
581 sugar|honey
582 cooking_oil
583 brown_sugar
584 bagoong_alamang|guinamos
585 fried_garlic
586 yellow_mustard|dijon_mustard
590 ginger
591 water+salt
592 siling_labuyo
593 whole_milkfish
594 whole_chicken
595 unpeeled_garlic
596 whole_tilapia
597 siling_pangsigang
598 siling_pangsigang
599 rock_salt
601 mint_leaves
602 cilantro+nutmeg_powder
603 canned_green_jackfruit
604 curry_leaves|basil_leaf
605 lumpia_wrapper
606 fresh_taro_leaf
607 chicken_thigh_fillets
608 garlic_longganisa
609 boiled_peeled_shrimp
610 brown_sugar
611 lumpia_wrapper
612 tamarind_soup_base_mix
614 steamed_clam
615 mixed_vegetable
616 pork_shoulder
617 smoked_fish
618 saba_banana
619 broiled_chinese_eggplant
620 beef_broth|water
621 coconut_milk
622 dried_kale_leaf
623 garlic_fried_rice
624 garlic_fried_rice
625 dried_taro_leaf
626 cooled_cooked_white_rice
627 hard_boiled_egg
628 garlic
629 hard_boiled_egg
630 kaffir_lime_leaf
631 chicken
632 oxtail|tripe_unspecified_animal|beef
633 pork_hock|ham_hock
634 asian_long_eggplant
635 eddo_taro
636 tomato
637 birds_eye_chili
638 siling_labuyo
639 chorizo_de_bilbao
640 corn_on_the_cob
641 siling_pangsigang
642 siling_pangsigang
643 hard_boiled_egg
644 green_finger_chili
645 chorizo_macau
646 siling_labuyo
647 thai_chili|birds_eye_chili
648 garlic
649 boneless_skinless_chicken_thigh_meat
650 chicken_leg|chicken_thigh|whole_chicken
651 chicken_wing_drumettes_and_flats
653 pork_shank
654 butterflied_whole_chicken
655 ripe_saba_banana
656 salmon_head
657 pork_embutido
658 lemongrass
659 cooked_pork_barbecue
660 annatto_oil
661 siling_labuyo
662 coriander_seed|caraway_seed
663 ladys_choice_mayonnaise
664 white_miso|yellow_miso
665 sesame_oil
666 vegetable_oil
667 white_sugar|brown_sugar
670 beef_shank+beef_bone
671 red_chili+green_chili
672 cream_dory_fillet
673 heart_of_palm
674 batwan|kamias
675 siling_pangsigang
676 cornstarch
677 muscovado_sugar
678 quick_melt_cheese|sharp_cheddar_cheese
679 white_sugar
680 skinless_chicken_breast
681 cooked_sisig
682 wonton_wrapper
683 chicken_back_bone
684 fresh_miki_noodles
685 white_sweet_potato|orange_sweet_potato
686 cooked_linguine
687 baguio_lime_juice
688 bone_in_pork_chop
689 chicken_leg_quarter
690 mud_crab_claw
691 high_smoke_point_cooking_oil
692 eggplant
693 ice_cold_water
694 rice_wash
695 water
696 hard_boiled_egg
697 filipino_style_hotdog
698 siling_pangsigang
699 kaffir_lime_leaf
700 heated_flour_tortilla
701 whole_chicken
702 lemongrass_bulb
703 steamed_mantou_bun
704 red_tomato
705 ham_slices
706 okra
707 white_fish_steak
708 siling_labuyo
709 boneless_chicken_breast
710 chicken_leg_quarter
711 hard_boiled_egg
712 green_bell_pepper+red_bell_pepper
713 siling_pangsigang
714 lemongrass_bulb
715 siling_pangsigang
716 okra
717 pork_chop
718 saba_banana
719 smoked_galunggong_flakes
720 thai_chili|siling_labuyo
721 white_fish_fillet
722 whole_pork_leg
723 celery
724 banaba_tea
725 chayote
726 kinchay
727 lemongrass
728 aligue_paste
729 reserved_cooked_duck_adobo_marinade
730 ladys_choice_real_mayonnaise
731 red_wine_vinegar
732 iloko_vinegar
733 cracked_peppercorn
735 fried_egg
736 cooked_bacon
737 tilapia_fillet
739 chicken_wing+chicken_leg+chicken_thigh
740 pork_belly
741 glutinous_rice
742 spanish_bomba_rice|calrose_rice
743 napa_cabbage_leaf
744 pandan_leaf
745 siling_labuyo
746 siling_pangsigang
747 siling_labuyo
749 lemongrass
751 cracked_black_peppercorn
752 siling_labuyo
753 rehydrated_dried_shiitake_mushroom+hot_water
754 beef_rump_steak
755 squash
756 salted_talimusak
757 beef_kneecap
758 beef_sirloin
759 mixed_chicken_parts
760 chicken_bone+chicken_meat
761 skin_on_boneless_chicken_breast
762 clam
763 tilapia_fillet
764 grouper_fillet
765 mackerel
766 oyster_mushroom
767 skin_on_pork_belly
768 pork_sinigang_cut
769 prawn_with_heads_reserved
770 salmon_steak
771 peeled_deveined_shrimp_tail_on
772 squid_with_tentacles
773 spider_crab
774 extra_firm_tofu|tempeh
775 bone_in_center_cut_pork_loin_rib_chop
777 sunny_side_up_egg
778 green_bell_pepper|poblano_chili
779 spring_onion_stalk
780 fried_egg
781 saba_banana
782 hard_boiled_egg|hard_boiled_quail_egg
783 fried_saba_banana
784 siling_pangsigang
785 siling_pangsigang
786 peeled_tiger_prawn_head_tail_on
787 pork_butt
788 sausage
789 lemongrass
790 tamarind
791 cooked_peeled_headless_shrimp
792 peeled_headless_deveined_shrimp
793 young_coconut_meat
794 chicken_leg+chicken_thigh
795 reserved_beef_tripe_broth
796 mustard_leaves
797 pork_loin
798 garlic
799 rice_wash
800 japanese_corn_kernel
801 napa_cabbage_leaf
802 pancit_canton_noodle
803 green_bean
804 soaked_dried_red_chili
805 guava
806 peeled_deveined_shrimp_tail_on
807 dried_kamias|fresh_kamias
808 red_chili
809 ampalaya_leaves
810 fish_sauce
811 active_dry_yeast
812 bagoong_alamang
814 banana_leaf
815 black_pepper
816 water+salt
817 calamansi_juice
818 canola_oil
819 canola_oil
820 chili_flake
821 chili_sauce
822 siling_labuyo
824 steamed_manila_clam_meat
825 young_coconut_meat
826 coconut_cream
827 cooking_oil
828 corn_on_the_cob
829 crispy_fried_garlic
830 dried_mexican_oregano
831 crispy_shallot
832 calamansi_juice
833 salted_talimusak
834 fish_sauce
836 cilantro
837 fried_pork_belly
838 fried_garlic
839 garlic_chip
840 garlic_fried_rice
841 green_lettuce_leaf
842 chili_leaves
843 hot_cooking_oil
844 lemon_juice
845 lime_juice|calamansi_juice
846 lemon_juice
847 lime_juice
848 kinchay
849 chive
850 kangkong_leaves
851 lemongrass_stalks
852 mango_flesh
853 masago
856 nori
857 nori
858 cooking_oil
859 cooking_oil
860 leek
861 brown_sugar
862 presoaked_banana_heart
863 soy_sauce+chili_unspecified_variety+calamansi
864 parsley
865 pasotes_leaf
866 pepper_flake_unspecified_type
867 pineapple_chunk
868 prawn_head
869 siling_labuyo
870 rock_salt
871 salt
872 salt+ground_pepper_unspecified_type
873 salt+pepper_unspecified
874 salt
875 sea_salt+ground_pepper_unspecified_type
876 crispy_fried_shallot
877 shrimp_head
878 siling_labuyo
879 sinigang_mix|crushed_tamarind
880 soy_calamansi_dip
881 spring_onion
882 sugar
885 vegetable_oil
886 vegetable_oil
887 vegetable_oil
888 vinegar_soy_sauce_dip
889 warm_corn_tortilla
890 water
891 water
892 water
'''

def leaf(name):
    # Reuse catalogued exact-name aliases (e.g. patola -> sponge_gourd).
    canonical = vocabulary.get(name.replace('_', ' '), name)
    return {'ingredient_id': canonical}

def expression(text):
    if '|' in text:
        return {'any_of': [expression(x) for x in text.split('|')]}
    if '+' in text:
        return {'all_of': [leaf(x) for x in text.split('+')]}
    return leaf(text)

decisions = {}
for reading in READINGS.strip().splitlines():
    number, food = reading.split(' ', 1)
    i = int(number)
    assert i not in decisions, i
    exp = expression(food)
    names = food.replace('+', ' together with ').replace('|', ' OR ').replace('_', ' ')
    decisions[i] = {
        'ingredient_line': rows[i]['ingredient_line'],
        'status': 'resolved',
        'requirement': exp,
        'basis': f'Semantic reading: {names}. Quantities and ordinary cutting/serving directions remain in the retained source; explicitly named food forms and choices are represented here.',
    }

def override(i, exp, basis, status='resolved'):
    decisions[i] = {'ingredient_line': rows[i]['ingredient_line'], 'status': status, 'requirement': exp, 'basis': basis}

# Nested alternatives must remain nested instead of becoming multiple compulsory foods.
override(265, {'any_of': [leaf('annatto_powder'), {'all_of': [leaf('annatto_seed'), leaf('water')]}]},
         'Source explicitly permits annatto powder OR seeds steeped in water; the seed-and-water preparation is a single alternative.')
override(322, {'any_of': [leaf('pork_belly'), leaf('peeled_headless_shrimp')]},
         'Malformed list punctuation suggests both proteins, but supplied Guisadong Monggo instructions explicitly say "Add pork or shrimps". Preserve that choice; the later separate liempo line remains separately required.')
override(652, {'any_of': [{'all_of': [leaf('goat_head'), leaf('goat_foot')]}, leaf('goat_meat_unspecified_part')]},
         'Source gives goat head AND feet as one traditional combination, OR other unspecified goat parts; neither a specific extra cut nor a requirement for every cut is invented.')
override(776, {'any_of': [leaf('chicken_stock'), {'all_of': [leaf('water'), leaf('chicken_bouillon_cube')]}]},
         'Explicit choice of chicken stock OR water combined with a chicken bouillon cube.')

# Equipment is retained as equipment and cannot be recommended as edible food.
override(813, None, 'Bamboo sticks/pangtusok are skewering equipment, not an edible ingredient.', 'non_ingredient')
decisions[813]['equipment_requirement'] = {'equipment_id': 'bamboo_skewer'}
override(854, None, 'Source explicitly permits either metal or soaked bamboo skewers; these are equipment.', 'non_ingredient')
decisions[854]['equipment_requirement'] = {'any_of': [{'equipment_id': 'metal_skewer'}, {'equipment_id': 'bamboo_skewer'}]}
override(823, None, 'Detached advice about selecting thigh meat repeats the immediately preceding chicken thigh-or-leg ingredient; it is not an additional ingredient line.', 'non_ingredient')
override(835, None, '"For the main dish" is a section heading, not a food or quantity.', 'non_ingredient')
override(855, None, 'Detached modern-cut explanatory note under the preceding goat-meat ingredient. The companion traditional note and this note describe alternative variants, not two additional obligatory meats.', 'non_ingredient')
decisions[855]['ingredient_variant_note'] = {'any_of': [leaf('goat_shoulder'), leaf('goat_leg')]}
override(884, None, 'Detached traditional-cut note under goat meat; "up and down" is corrupted prose. The recoverable head/feet examples are variant advice, not a new separately required ingredient.', 'non_ingredient')
decisions[884]['ingredient_variant_note'] = {'all_of': [leaf('goat_head'), leaf('goat_foot')]}

# Explicit evidence from the supplied instructions resolves extraction errors and vague nouns.
BASIS = {
  3: 'Fresh ginger is listed twice in different shapes; the concatenated "46" quantity is not a new ingredient. Source quantities remain unchanged.',
  12: 'Rice is explicitly ground and toasted; retain that prepared form, without assuming raw rice and rice flour are universally equivalent.',
  23: 'Source explicitly combines coconut-milk powder with water; neither is discarded.',
  27: 'Bell pepper is the named ingredient; "siling pula" specifies its red color here rather than adding a separate hot chili.',
  30: 'Source permits baby or regular size of bok choy; these are size variants of the named vegetable, not a second plant species.',
  51: 'Sprite is an example of the permitted similar soda; preserve lemon-lime soda category rather than requiring a brand.',
  53: 'Chicken bouillon cube is explicitly dissolved in water and reduced. Retain both ingredients; reduction is preparation, not a different meat stock.',
  55: 'Conflicting age words are resolved by explicit "use mature ... niyog"; this is shredded mature coconut meat, not tender young buko.',
  57: 'Flour is explicitly seasoned with salt, unspecified pepper and sinigang-sa-kamias powder, all retained as components.',
  60: 'Breadcrumbs and the explicitly added kamias sinigang powder are both retained.',
  69: 'Source explicitly allows shrimp, prawns, or a prepared mixed-seafood assortment including fish balls and crabsticks. The assortment is not collapsed to shrimp alone.',
  70: 'Galapong is the explicit alternative to glutinous-rice flour; it is not declared universally identical to dry flour.',
  74: 'Medium grain rice is stated; no variety or cooked state is invented.',
  77: 'Ingredient is generic vinegar, with white/cane only preferred. Keep generic unspecified vinegar; preference text remains in source.',
  82: 'Lengua Estofado instructions reserve liquid specifically from simmering beef tongue with aromatics. This is reserved beef-tongue broth, not arbitrary stock.',
  84: 'Dinorado is the specifically named rice variety; retain that identity despite an imprecise short-grain gloss, without asserting all short-grain rice is Dinorado.',
  88: 'Source explicitly says string OR green beans, so retain the choice rather than forcing botanical equivalence.',
  91: 'Generic vinegar is required; apple cider is a permitted example, not an additional required ingredient.',
  93: 'Named white miso is a fermented soybean seasoning; its ground-soybean gloss does not replace it with unfermented beans.',
  111: 'Mackerel is explicitly named with the local hasa-hasa example; no particular mackerel species is fabricated.',
  118: 'Chicken legs/thighs names alternative cuts; no requirement to have both cuts is inferred from the slash.',
  122: 'Source names hiwas, sapsap, bisugo and galunggong as fish options and says cleaned and salted. Retain salted species alternatives; none are equated.',
  127: 'The parenthesis explicitly permits kasim OR liempo despite the inaccurate overarching belly gloss. Preserve shoulder/belly as alternatives.',
  130: 'Buto-buto means bony pork pieces; do not normalize to boneless pork meat.',
  138: 'Tilapia Curry instructions consistently use fish fillets; the whole tilapias option explicitly says filleted. Both procurement routes produce tilapia fillet.',
  160: 'Honeycomb tripe is named, but the source line does not identify an animal. No beef species is imposed without context.',
  166: 'Baguio beans explicitly identifies green/snap beans despite loose long-bean wording. No universal equivalence with sitaw is introduced.',
  188: 'Palabok noodles are explicitly described as cornstarch sticks; preserve the named palabok noodle product.',
  189: 'Rice noodles have been soaked until soft, then drained; soaking is not assumed to mean cooked.',
  198: 'Beef cube OR pork cube refers to alternative seasoning/bouillon cubes, not raw meat cubes.',
  206: 'The source explicitly retains fish scales while removing the guts; that preparation constraint is kept in the identity.',
  211: 'Crispy Pata context, whole serving and reference to removal from the bone identify the unnamed pork as a pork leg. It is not arbitrary pork mince or belly.',
  215: 'Ground beef is the ingredient; 80/20 is explicitly recommended, not compulsory. Its ratio preference remains in the source.',
  217: 'Fish fillet is generic, with herring/tamban only recommended; no mandatory species is imposed.',
  220: 'Kinunot instructions explicitly add first-press milk from one coconut; resolve the truncated "1 press milk" as first-press coconut milk.',
  229: 'Pork Sinigang sa Mangga calls the slab lechon-kawali cut, tenderized, then instructs frying cubed pork. Retain tenderized pork belly, not already-fried lechon kawali.',
  248: 'Annatto seeds are explicitly steeped in pork broth; both source ingredients are preserved.',
  260: 'The powder explicitly comes from sinigang-sa-sampalok mix, a formulated soup base rather than pure tamarind fruit powder.',
  261: 'Tomato paste is explicitly named; the misleading pino-na-kamatis gloss does not turn it into fresh chopped tomato.',
  266: 'The source gives an equivalent amount of shrimp bouillon without requiring a cube shape; retain bouillon, not fresh shrimp.',
  282: 'Whole chicken is required; air-chilled is a recommendation for texture, retained in original text rather than an obligatory substitute identity.',
  286: 'A whole garlic head is a quantity unit, not an edible ingredient distinct from garlic cloves; halving is a knife-cut instruction.',
  288: 'A head is a quantity unit; despite the minced/crushed wording variation the ingredient is garlic.',
  300: 'Supplied Bangus sa Tausi instructions explicitly mix flour, salt and pepper for coating. This line is all-purpose flour; the erroneous appended "paminta sa pagmamasa" is a mistranslated gloss, with pepper listed separately.',
  304: 'Canola oil is the supplied ingredient for later making atsuete oil. Do not replace it with already prepared annatto oil or invent seeds in this line.',
  305: 'Preserve the explicitly named Filipino kinchay; the Chinese-parsley gloss is not used to assert interchangeability with cilantro or Western parsley.',
  306: 'Coconut cream is explicitly named; loose gata gloss does not remove its cream form.',
  320: 'Ground peanuts made into paste are retained as peanut paste; this is not an assertion that commercial sweetened peanut butter is equivalent.',
  327: 'Source permits softened butter OR margarine. Softening is preparation retained in original text; the two products remain alternatives.',
  331: 'Tapuy is named as one option alongside generic rice wine, without declaring every rice wine to be tapuy.',
  362: 'A malformed parenthesis contains two explicit ingredients: squash, then 500 grams potato marbles. Preserve both instead of losing the baby potatoes.',
  374: 'Hibi is explicitly dried shrimp ground to powder; preserve both dried and ground form.',
  377: 'Rock OR ground salt are the stated options; the malformed fraction affects quantity only and remains in original text.',
  382: 'Chicharo is the named edible pea pod; use snow pea identity without turning it into dried peas.',
  387: 'Source specifies fish paste bagoong, so use fish bagoong rather than shrimp paste.',
  395: 'Rice has been toasted and pounded to powder; retain ground toasted rice rather than treating every rice ingredient as interchangeable.',
  398: 'The Pork Isaw Satay instructions reserve prepared spice paste from the marinade for frying into peanut sauce. Keep this prepared subrecipe as fried spice paste; no unknown spice formula is invented.',
  399: 'Source explicitly insists on Filipino vinegar but leaves its type unspecified; preserve that regional category without choosing cane or coconut vinegar.',
  401: 'Turmeric is explicitly soaked in measured water; preserve both named components.',
  402: 'Source specifically selects sirloin and explicitly marinates it with soy sauce and calamansi; those ingredients are retained, not inferred from the dish name.',
  408: 'Source says tripe/tuwalya but not the animal; salt used to scrub is explicitly retained, without inventing beef.',
  411: 'Sitaw explicitly disambiguates the loose English green-bean label as yardlong beans.',
  415: 'Misua is the specifically named noodle; retain that product identity rather than trusting the inaccurate rice-noodle gloss.',
  422: 'Tagalog instructions say peel/devein the shrimp and reserve its shell. Keep both peeled shrimp and retained shrimp shell.',
  431: 'Source explicitly permits tamarind soup-base powder OR fresh tamarind fruit. They remain different alternatives.',
  443: 'Baguio beans explicitly specifies green/snap beans despite generic long-green-bean wording.',
  444: 'Baguio beans explicitly specifies green/snap beans despite generic long-green-bean wording.',
  454: 'Source specifies sweet-potato leaves with their stalks; do not substitute the starchy tuber.',
  455: 'Pechay is the local named ingredient; generic Chinese-cabbage gloss does not imply pechay Baguio/napa.',
  467: 'Source explicitly reserves the broth from cooking chicken, so retain reserved chicken broth rather than raw chicken or generic water.',
  473: 'Seafood Gising-Gising instructions explicitly add kangkong stalks; this resolves the extraction-conflicted leaves/stalks wording to stalks.',
  475: 'Source states the actual assortment used: kangkong, eggplant, okra and tomatoes. All four are retained rather than assigning generic vegetables only.',
  477: 'Filipino-style Pineapple Glazed Ham instructions reserve the ham poaching liquid made earlier; retain that prepared internal ingredient, not plain water or arbitrary broth.',
  484: 'Source line combines coloring and ube flavoring; supplied Ginataang Halo Halo instructions explicitly say purple ube coloring and flavoring. Preserve both named preparation components.',
  491: 'The two malformed jalapeo/jalapeos words repeat the same quantified jalapeno ingredient; they are not two separate foods.',
  503: 'Pig tails are explicitly named; the instruction that they will be called pork later does not erase the cut.',
  504: 'Source explicitly selects wahoo/tanigue fillet; preserve named species and fillet form.',
  519: 'Tagalog "gumamit ng hita ng manok" explicitly selects chicken thigh rather than unspecified chicken.',
  535: 'Thick-cut fish fillet is the required source head. Skin-on wild-caught snapper is explicitly recommended, so that species-and-skin preference is retained as metadata instead of being made compulsory.',
  539: 'Instructions repeatedly cook beef shanks, resolving the inaccurate litid gloss. Preserve boneless beef shank, not isolated tendon.',
  562: 'Both white and green parts come from the stated leeks; different cutting lengths do not create separate ingredient identities.',
  570: 'The optional addition explicitly permits dried shrimp OR finely chopped meat of unspecified animal. Preserve the option and do not invent pork.',
  573: 'Reno is an example of liver spread, with similar products allowed; generic liver spread is the requirement.',
  574: 'Neutral cooking oil is required; grapeseed is only an example, not the sole acceptable oil.',
  576: 'The explicitly named peanut butter is supported by sauce context; erroneous "mantika ng mani" gloss does not turn it into peanut oil.',
  578: 'Toasted rice flour is the explicit form; the loose galapong gloss does not change this into an obligatory wet dough.',
  583: 'Brown sugar is the stated ingredient; maskobado is its source gloss/example and does not create an additional sugar requirement.',
  591: 'Both water and the explicitly added salt are retained as the brine mixture.',
  606: 'Fresh taro leaves are specified; the source intact/no-holes selection constraint remains in original text, with no dried-leaf equivalence.',
  608: 'Garlic longganisa is the product category; Cabanatuan, Cebu, Vigan and Tuguegarao are example varieties rather than four required sausages.',
  612: 'Maggi is explicitly an example of tamarind soup-base mix; no compulsory brand is inferred.',
  621: 'Gata is a translation of the specifically named coconut milk in this line, not another alternative ingredient.',
  631: 'Generic chicken pieces are required; legs/thighs are explicitly preferred, with that preference preserved in source rather than made compulsory.',
  632: 'Source explicitly offers oxtail, tripe or beef slices as alternatives. It does not explicitly name the tripe animal, so no species is fabricated for that option.',
  634: 'Asian long eggplant is explicitly named, not an assertion of interchangeability with all eggplant varieties.',
  660: 'The food ingredient is annatto oil. A misplaced bamboo-skewer soaking note is equipment preparation and does not add bamboo as food.',
  670: 'Beef shank is explicitly supplemented with extra bones, so retain both meat cut and additional beef bones.',
  672: 'Source explicitly says use fillets despite the conflicting counting phrase "3 whole cream dory"; preserve cream-dory fillet form.',
  674: 'Batwan OR kamias are explicit alternatives. The aside about where to find preserved/powdered batwan is shopping advice, not a new required ingredient.',
  687: 'Baguio limes are squeezed; retain juice from that named citrus rather than silently substituting calamansi.',
  690: 'Source specifically uses claws from alimango/mud crab; preserve the claw part.',
  700: 'Adobo Burrito instructions layer fillings on, then roll the "burrito" wrapper. The extracted phrase means heated large flour tortillas, not an additional filled burrito.',
  703: 'Mantou buns are explicitly steamed according to package directions; keep the steamed product form.',
  707: 'White-fish steaks are required; maya-maya is introduced as an example, not a compulsory species.',
  710: 'The specified quarters comprise leg and thigh, even when separated; retain the leg-quarter cut.',
  721: 'Source says white fish fillets, with cream dory/lapu-lapu as examples. Retain the broad required class rather than insisting on either exemplar.',
  726: 'Preserve the explicitly named kinchay rather than treating the Chinese-parsley gloss as universal equivalence with cilantro.',
  729: 'Duck Adobo instructions cook the duck with its marinade, then use that reserved mixture for rice. Retain reserved cooked duck-adobo marinade as an internal prepared component.',
  735: 'Fried eggs are required; the linked comment about ten other cooking methods is promotional advice, not ten alternative compulsory egg products.',
  753: 'Source explicitly rehydrates dried shiitake in hot water. The prepared mushroom form and stated soaking water are represented.',
  756: 'Talimusak/goby is explicitly salted; retain the seasoned fish form.',
  761: 'Source explicitly requires boneless chicken breast while keeping skin on; do not merge with skinless fillet.',
  763: 'Tagalog says tilapia was used in this recipe, selecting tilapia fillet rather than an unspecified mandatory species.',
  765: 'Alumahan is offered as an ordinary local mackerel option; preserve the mackerel category without asserting a uniquely identified species.',
  769: 'Prawns are used and half their heads are reserved. Retain that source form, avoiding a headless-prawn normalization.',
  772: 'Source explicitly reserves the squid tentacles; the identity retains them rather than interpreting cleaning as their removal.',
  773: 'Spider crab is explicitly named; the loose alimasag gloss is not used to universally equate spider crab with every blue crab.',
  782: 'Source explicitly offers hard-boiled chicken eggs for tokneneng OR hard-boiled quail eggs for kwek-kwek. They are alternative preparations, never all required.',
  795: 'Goto instructions reserve strained broth from cooking beef tripe and beef bones with aromatics. Retain this internal beef-tripe broth, not arbitrary broth.',
  798: 'Garlic is peeled and smashed while left as whole cloves; "whole" describes cloves, not unpeeled heads.',
  803: 'Baguio beans is the explicit local name, interpreted as green/snap beans; generic string-bean gloss does not force equivalence with sitaw.',
  824: 'Source obtains clam meat from steamed Manila clams; retain species, meat-only part and cooked state.',
  825: 'Source explicitly calls the coconut buko and selects its spoon-scraped meat. Retain young coconut meat rather than replacing it with mature niyog.',
  826: 'Kakang gata is explicitly coconut cream in this line; retain cream concentration, not plain coconut milk.',
  833: 'Tagalog says cleaned and salted talimusak. It is the same named seasoned goby-fish product rather than an untranslated prose slug.',
  837: 'Source explicitly calls for fried pork-belly slices; do not reduce this to generic raw pork or detached pork skin.',
  848: 'Kinchay is preserved as the named local herb; the generic parsley gloss does not authorize substituting Western parsley or cilantro.',
  862: 'Banana heart/puso ng saging is explicitly presoaked; retain that vegetable form, not banana fruit.',
  863: 'The optional accompaniment explicitly contains soy sauce, chopped unspecified chili and calamansi; all named components are retained.',
  868: 'Only prawn heads are used and crushed. Preserve the head part without adding prawn meat.',
  872: 'Salt AND ground pepper are both present; pepper type is unspecified and not automatically black pepper.',
  875: 'Sea salt AND freshly ground pepper are both present; pepper species is unspecified.',
  879: 'Source explicitly permits sinigang mix OR crushed tamarind fruit; a formulated mix is not declared identical to the fruit.',
  888: 'Vinegar-soy sauce is an explicitly named prepared serving dip, not a new type of vinegar.',
}
for i, basis in BASIS.items():
    decisions[i]['basis'] = basis
decisions[484]['requirement'] = {'all_of': [leaf('ube_food_flavoring'), leaf('purple_food_coloring')]}
decisions[535]['preferred_ingredient'] = leaf('skin_on_wild_caught_snapper_fillet')

# Preserve the author's leading food noun while flagging an imprecise parenthetical
# culinary gloss. This does NOT create a global alias or add a substitution option.
def terminology(i, primary, gloss):
    override(i, leaf(primary), f'The explicit leading source food noun is {primary.replace("_", " ")}; assign that identity only. Preserve the appended {gloss!r} gloss for terminology review, without asserting botanical identity or allowing an unrequested substitute.')
    decisions[i]['source_gloss'] = gloss
    decisions[i]['terminology_review_required'] = True

for i in [100,102]:
    terminology(i, 'green_bell_pepper', 'berdeng siling pangsigang')
for i in [223,224]:
    terminology(i, 'red_bell_pepper', 'pulang siling pangsigang')
terminology(146, 'bok_choy', 'pechay baguio')
for i in [419,420,588,589,600,668,669,734,738,748]:
    terminology(i, 'thai_chili', 'siling labuyo')
terminology(440, 'red_thai_chili', 'siling labuyo')
terminology(613, 'siling_labuyo', 'Thai bird\u2019s eye chilies')
terminology(553, 'siling_pangsigang', 'thai chili peppers')
for i in [587,750,883]:
    terminology(i, 'thai_chili', 'siling pangsigang')

for i, gloss in [(84, 'short grain'), (93, 'ground soy beans'), (261, 'pino na kamatis'),
                 (305, 'Chinese parsley'), (306, 'gata'), (415, 'fine rice noodles'),
                 (539, 'litid ng baka'), (576, 'mantika ng mani'), (578, 'galapong'),
                 (579, 'alamang'), (583, 'maskobado'), (726, 'Chinese parsley'),
                 (773, 'alimasag'), (848, 'parsley')]:
    decisions[i]['source_gloss'] = gloss
    decisions[i]['terminology_review_required'] = True

missing = sorted(set(range(len(rows))) - set(decisions))
assert not missing, f'Missing decision indexes: {missing}'
assert len(decisions) == len(rows) == 893
for i, decision in decisions.items():
    decision['annotation_type'] = 'ai_semantic_annotation'
    decision['reviewer'] = 'Codex parallel semantic annotation; not independent human review'
out = [decisions[i] for i in range(len(rows))]
path = ROOT / 'partition_01.decisions.json'
path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(Counter(x['status'] for x in out))
print('Assigned source lines:', len(rows), 'decisions:', len(out))

def ids(exp):
    if not exp:
        return set()
    if 'ingredient_id' in exp:
        return {exp['ingredient_id']}
    return set().union(*(ids(e) for k in ['all_of', 'any_of'] for e in exp.get(k, [])))
new = sorted(set().union(*(ids(d.get('requirement')) for d in out)) - known)
(Path(__file__).parent / 'new_ids.txt').write_text('\n'.join(new), encoding='utf-8')
print('Named food/form IDs outside initial vocabulary:', len(new))
print('Output:', path)
