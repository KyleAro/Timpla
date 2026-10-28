"""Commands for reviewing data, training, and running the recipe ranker."""
import argparse
import json
from pathlib import Path
import sys

from ranker import (read_json, validate_recipes, candidates, candidate_result,
                    review_queue, train, recommend)

ROOT = Path(__file__).resolve().parent


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recipes', type=Path, default=ROOT/'data/recipes.review.json')
    parser.add_argument('--aliases', type=Path, default=ROOT/'data/aliases.json')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('audit', help='Validate proposed records and report pending human reviews')
    queue = commands.add_parser('review-queue', help='Create blank human relevance-label CSV; never overwrites')
    queue.add_argument('--queries', type=Path, default=ROOT/'data/queries.review.json')
    queue.add_argument('--output', type=Path, default=ROOT/'data/relevance.review.csv')
    fit = commands.add_parser('train', help='Fit only after recipe, query and relevance review is complete')
    fit.add_argument('--queries', type=Path, default=ROOT/'data/queries.review.json')
    fit.add_argument('--labels', type=Path, default=ROOT/'data/relevance.review.csv')
    fit.add_argument('--output', type=Path, required=True)
    for command in ('preview','recommend'):
        sub = commands.add_parser(command, help='Preview eligible candidates' if command=='preview' else 'Rank using a trained model')
        sub.add_argument('--ingredients', nargs='+', required=True)
        sub.add_argument('--use-first', nargs='*', default=[])
        sub.add_argument('--excluded', nargs='*', default=[])
        sub.add_argument('--max-minutes', type=float)
        sub.add_argument('--region', default='')
        if command == 'recommend':
            sub.add_argument('--model', type=Path, required=True)
            sub.add_argument('--limit', type=int, default=5)
    args = parser.parse_args(argv)
    try:
        recipes, aliases = read_json(args.recipes), read_json(args.aliases)
        if args.command == 'audit':
            validate_recipes(recipes, aliases, require_review=False)
            pending = [r['id'] for r in recipes if not r.get('reviewed_by','').strip() or not r.get('reviewed_at','').strip()]
            output = {'recipes':len(recipes),'pending_recipe_review':pending,'ready_for_training':False,
                      'note':'Recipe review and human relevance labels are required; this audit does not train a model.'}
        elif args.command == 'review-queue':
            count = review_queue(recipes,read_json(args.queries),aliases,args.output)
            output = {'unlabeled_pairs':count,'path':str(args.output),'note':'Draft queue: review recipe ingredient roles, query scenarios and rankings before training.'}
        elif args.command == 'train':
            output = train(recipes,read_json(args.queries),args.labels,aliases,args.output,
                           [args.recipes,args.aliases,args.queries,args.labels])
        else:
            query = {'available':args.ingredients,'use_first':args.use_first,'excluded':args.excluded,
                     'max_minutes':args.max_minutes,'preferred_region':args.region}
            if args.command == 'preview':
                validate_recipes(recipes,aliases,require_review=False)
                output = {'mode':'unranked_review_preview_not_model_prediction',
                          'candidates':[candidate_result(r,query,aliases) for r in candidates(recipes,query,aliases)],
                          'note':'Ingredient roles are provisional until human review. No trained ranking is used.'}
            else:
                output = {'recommendations':recommend(recipes,query,aliases,args.model,args.limit)}
        print(json.dumps(output,indent=2,ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, ImportError) as error:
        print(f'Cannot continue: {error}',file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
