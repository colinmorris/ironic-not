import itertools

subjects = "me,you,them".split(',')
verbs = "thinking,taking,using,trying,acting".split(',')

phrase_ids = [
        f'not_{subj}_{verb}'
        for (subj, verb) in itertools.product(subjects, verbs)
]

phrase_ids += ['lmao_not', 'omg_not']
