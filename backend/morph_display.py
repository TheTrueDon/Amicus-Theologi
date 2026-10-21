"""Conservative display translation. Original source codes always remain available.
Known Robinson/Byzantine-style Greek codes and OSHB morphological codes.
No heuristic guesses for unknown tagging standards.
"""
import re
G_POS={'N':'Substantiv','V':'Verb','A':'Adjektiv','P':'Pronomen','R':'Pronomen','T':'Artikel','D':'Adverb','C':'Konjunktion','PREP':'Präposition','CONJ':'Konjunktion','ADV':'Adverb','INJ':'Interjektion'}
G_CASE={'N':'Nominativ','G':'Genitiv','D':'Dativ','A':'Akkusativ','V':'Vokativ'}
G_NUM={'S':'Singular','P':'Plural'}
G_GEN={'M':'Maskulinum','F':'Femininum','N':'Neutrum'}
G_TENSE={'P':'Präsens','I':'Imperfekt','F':'Futur','A':'Aorist','R':'Perfekt','L':'Plusquamperfekt','2A':'2. Aorist','2F':'2. Futur','2R':'2. Perfekt','2L':'2. Plusquamperfekt'}
G_VOICE={'A':'Aktiv','M':'Medium','P':'Passiv','E':'Medium/Passiv','D':'Deponens','O':'Medium/Passiv'}
G_MOOD={'I':'Indikativ','S':'Konjunktiv','O':'Optativ','M':'Imperativ','N':'Infinitiv','P':'Partizip'}
H_POS={'V':'Verb','N':'Substantiv','A':'Adjektiv','P':'Pronomen','R':'Präposition','C':'Konjunktion','D':'Adverb','T':'Partikel','S':'Suffix'}
H_STEM={'q':'Qal','N':'Nifal','p':'Piel','P':'Pual','h':'Hifil','H':'Hofal','t':'Hitpael','o':'Polel','O':'Polal','r':'Hitpolel','m':'Poel','M':'Poal','k':'Palel','K':'Pulal','Q':'Qal Passiv','l':'Pilpel','L':'Polpal','f':'Hitpalpel','D':'Nithpael','j':'Pealal','i':'Pilel','u':'Hothpaal','c':'Tiphil','v':'Hishtaphel','w':'Nithpalel','y':'Nithpoel','z':'Hitpoel'}
H_CONJ={'p':'Perfekt (Suffixkonjugation)','q':'Perfekt (Suffixkonjugation)','i':'Imperfekt (Präfixkonjugation)','w':'Waw-konsekutiv / Wayyiqtol','h':'Kohortativ','j':'Jussiv','v':'Imperativ','r':'Partizip aktiv','s':'Partizip passiv','a':'Infinitiv absolut','c':'Infinitiv constructus'}
H_GENDER={'m':'Maskulinum','f':'Femininum','c':'Gemeinsames Genus'}
H_NUM={'s':'Singular','p':'Plural','d':'Dual'}

UD_POS={'NOUN':'Substantiv','PROPN':'Eigenname','VERB':'Verb','AUX':'Hilfsverb',
        'ADJ':'Adjektiv','ADV':'Adverb','PRON':'Pronomen','DET':'Determinativ/Artikel',
        'ADP':'Präposition','CCONJ':'nebenordnende Konjunktion','SCONJ':'unterordnende Konjunktion',
        'PART':'Partikel','NUM':'Zahlwort','INTJ':'Interjektion','PUNCT':'Interpunktion',
        'SYM':'Symbol','X':'nicht bestimmbar'}
UD_FEATURE={'Case':{'Nom':'Nominativ','Gen':'Genitiv','Dat':'Dativ','Acc':'Akkusativ','Voc':'Vokativ',
                    'Abl':'Ablativ','Loc':'Lokativ'},
            'Number':{'Sing':'Singular','Plur':'Plural','Dual':'Dual'},
            'Gender':{'Masc':'Maskulinum','Fem':'Femininum','Neut':'Neutrum','Com':'Gemeinsames Genus'},
            'Tense':{'Pres':'Präsens','Past':'Präteritum','Fut':'Futur','Pqp':'Plusquamperfekt'},
            'Mood':{'Ind':'Indikativ','Sub':'Konjunktiv','Imp':'Imperativ','Cnd':'Konditional'},
            'Voice':{'Act':'Aktiv','Pass':'Passiv','Mid':'Medium'},
            'Person':{'1':'1. Person','2':'2. Person','3':'3. Person'},
            'VerbForm':{'Fin':'finit','Inf':'Infinitiv','Part':'Partizip','Ger':'Gerundium','Gdv':'Gerundivum'},
            'Aspect':{'Imp':'imperfektiv','Perf':'perfektiv','Prosp':'prospektiv'},
            'Degree':{'Pos':'Positiv','Cmp':'Komparativ','Sup':'Superlativ'},
            'Definite':{'Def':'bestimmt','Ind':'unbestimmt'},
            'PronType':{'Prs':'Personal','Dem':'Demonstrativ','Rel':'Relativ','Int':'Interrogativ','Ind':'Indefinit'}}
UD_FEATURE_NAMES={'Case':'Kasus','Number':'Numerus','Gender':'Genus','Tense':'Tempus',
                  'Mood':'Modus','Voice':'Genus Verbi','Person':'Person',
                  'VerbForm':'Verbform','Degree':'Komparation','Definite':'Definitheit',
                  'PronType':'Pronominaltyp','Aspect':'Aspekt'}
AGDT_POS={'n':'Substantiv','v':'Verb','a':'Adjektiv','d':'Adverb','l':'Artikel',
          'r':'Pronomen','c':'Konjunktion','i':'Interjektion','e':'Ausruf',
          'p':'Präposition','m':'Zahlwort','g':'Partikel','x':'nicht bestimmbar',
          'u':'Wortart nicht bestimmt'}
AGDT_TENSE={'p':'Präsens','i':'Imperfekt','f':'Futur','a':'Aorist','r':'Perfekt','l':'Plusquamperfekt'}
AGDT_MOOD={'i':'Indikativ','s':'Konjunktiv','o':'Optativ','m':'Imperativ','n':'Infinitiv','p':'Partizip'}
AGDT_VOICE={'a':'Aktiv','m':'Medium','p':'Passiv','e':'Medium/Passiv'}
AGDT_DEGREE={'p':'Positiv','c':'Komparativ','s':'Superlativ'}

def _decode_ud(raw):
    bits=raw.split('|')
    pos=bits[0].strip().upper()
    if pos not in UD_POS:return None
    features=[{'name':'Wortart','value':UD_POS[pos]}]
    for bit in bits[1:]:
        if '=' not in bit:continue
        key,value=bit.split('=',1)
        decoded=UD_FEATURE.get(key,{}).get(value,value)
        features.append({'name':UD_FEATURE_NAMES.get(key,key),'value':decoded})
    return {'recognized':True,'features':features,'raw':raw,'scheme':'Universal Dependencies'}

def _decode_agdt(raw):
    if len(raw)!=9 or raw[0] not in AGDT_POS:return None
    pos,person,num,tense,mood,voice,gender,case,degree=raw
    features=[{'name':'Wortart','value':AGDT_POS[pos]}]
    if person in '123':features.append({'name':'Person','value':person+'. Person'})
    if num in {'s':'Singular','p':'Plural','d':'Dual'}:features.append({'name':'Numerus','value':{'s':'Singular','p':'Plural','d':'Dual'}[num]})
    if tense in AGDT_TENSE:features.append({'name':'Tempus','value':AGDT_TENSE[tense]})
    if mood in AGDT_MOOD:features.append({'name':'Modus','value':AGDT_MOOD[mood]})
    if voice in AGDT_VOICE:features.append({'name':'Genus Verbi','value':AGDT_VOICE[voice]})
    if gender.upper() in G_GEN:features.append({'name':'Genus','value':G_GEN[gender.upper()]})
    if case.upper() in G_CASE:features.append({'name':'Kasus','value':G_CASE[case.upper()]})
    if degree in AGDT_DEGREE:features.append({'name':'Komparation','value':AGDT_DEGREE[degree]})
    return {'recognized':True,'features':features,'raw':raw,'scheme':'AGDT/Perseus positional morphology'}

def decode(morph,language):
    raw=(morph or '').strip()
    if not raw:return {'recognized':False,'features':[],'notice':'Keine morphologischen Informationen angegeben.','raw':raw}
    if '+' in raw:
        parts=[decode(part,language) for part in raw.split('+')]
        features=[]
        for n,part in enumerate(parts,1):
            for feature in part.get('features',[]):
                features.append({'name':f'Teil {n}: {feature["name"]}','value':feature['value']})
        if features:return {'recognized':all(x.get('recognized') for x in parts),'features':features,
                           'raw':raw,'scheme':'Kompositanalyse'}
    if language in ('la','grc'):
        ud=_decode_ud(raw)
        if ud:return ud
        if language=='grc':
            agdt=_decode_agdt(raw.lower())
            if agdt:return agdt
        if raw.upper()=='X':
            return {'recognized':True,'features':[{'name':'Wortart','value':'nicht bestimmbar'}],
                    'raw':raw,'scheme':'Automatische Analyse: unbekannt'}
    features=[]
    def add(k,v):features.append({'name':k,'value':v})
    if language=='grc':
        # Typical Robinson: V-IAI-3S, N-NSM, V-PAP-NSM.
        s=raw.upper()
        if s.startswith('V-'):
            m=re.fullmatch(r'V-((?:2[AFRL]|[PIFARL]))([AMPEDO])([ISOMNP])(?:-([123])([SP])|-(?:([NGDAV])([SP])([MFN])))?',s.replace(' ',''))
            if m:
                tense,voice,mood,person,num,case,pnum,gen=m.groups()
                if tense in G_TENSE and voice in G_VOICE and mood in G_MOOD:
                    add('Wortart','Verb');add('Tempus',G_TENSE[tense]);add('Genus Verbi',G_VOICE[voice]);add('Modus',G_MOOD[mood]);
                    if person:add('Person',person+'. Person');add('Numerus',G_NUM[num])
                    if case:add('Kasus',G_CASE[case]);add('Numerus',G_NUM[pnum]);add('Genus',G_GEN[gen])
                    return {'recognized':True,'features':features,'raw':raw,'scheme':'Robinson-ähnliche griechische Morphologie'}
        m=re.fullmatch(r'([NATPR])-([NGDAV])([SP])([MFN])',s)
        if m:
            pos,case,num,gen=m.groups()
            add('Wortart',G_POS[pos]);add('Kasus',G_CASE[case]);add('Numerus',G_NUM[num]);add('Genus',G_GEN[gen])
            return {'recognized':True,'features':features,'raw':raw,'scheme':'Robinson-ähnliche griechische Morphologie'}
    if language=='he':
        return decode_hebrew(raw)
    return {'recognized':False,'features':[],'notice':'Codeformat derzeit nicht sicher erkannt. Der Originalcode bleibt erhalten; es wird keine Grammatik geraten.','raw':raw}

# Structure based on the published Open Scriptures Hebrew morphology code
# grammar. Composite codes use a single H/A prefix and slash-delimited
# prefixes, headword and (occasionally) suffixes, e.g. HC/R/Ncfsa.
_H_ADJECTIVE={'a':'Adjektiv','c':'Kardinalzahl','g':'Gentilizium','o':'Ordinalzahl'}
_H_PRONOUN={'d':'Demonstrativpronomen','f':'Indefinitpronomen','i':'Interrogativpronomen',
            'p':'Personalpronomen','r':'Relativpronomen'}
_H_PARTICLE={'a':'Bekräftigungspartikel','d':'Bestimmter Artikel','e':'Aufforderungspartikel',
             'i':'Fragepartikel','j':'Interjektion','m':'Demonstrativpartikel',
             'n':'Negationspartikel','o':'Akkusativmarker','r':'Relativpartikel'}
_H_SUFFIX={'d':'Direktional-He','h':'Paragogisches He','n':'Paragogisches Nun','p':'Pronominalsuffix'}


def _hebrew_part(part, aramaic=False):
    """Return guaranteed features for exactly one OSHB code, or None.

    Important: neither a generic morphological label (e.g. 'Prefix') nor an
    uncertain suffix is a dictionary translation. We do not infer meanings.
    """
    if not part:return None
    pos=part[0]; rest=part[1:]
    if pos not in H_POS:return None
    features=[('Wortart', H_POS[pos])]
    if pos=='V':
        if aramaic or len(rest)<2 or rest[0] not in H_STEM or rest[1] not in H_CONJ:return None
        features.extend([('Stamm',H_STEM[rest[0]]),('Form',H_CONJ[rest[1]])]);rest=rest[2:]
        if rest and rest[0] in '123':
            features.append(('Person',rest[0]+'. Person'));rest=rest[1:]
        if rest and rest[0] in H_GENDER:
            features.append(('Genus',H_GENDER[rest[0]]));rest=rest[1:]
        if rest and rest[0] in H_NUM:
            features.append(('Numerus',H_NUM[rest[0]]));rest=rest[1:]
        if rest and rest[0] in ('a','c','d'):
            features.append(('Status',{'a':'Absolutus','c':'Constructus','d':'Determiniert'}[rest[0]]));rest=rest[1:]
        if rest:return None
    elif pos in ('N','A'):
        types={'c':'Gattungsname','p':'Eigenname','g':'Gentilizium'} if pos=='N' else _H_ADJECTIVE
        if rest and rest[0] in types:
            features.append(('Typ',types[rest[0]]));rest=rest[1:]
        if rest and rest[0] in {**H_GENDER,'b':'Beide Genera'}:
            features.append(('Genus',{**H_GENDER,'b':'Beide Genera'}[rest[0]]));rest=rest[1:]
        if rest and rest[0] in H_NUM:
            features.append(('Numerus',H_NUM[rest[0]]));rest=rest[1:]
        if rest and rest[0] in ('a','c','d'):
            features.append(('Status',{'a':'Absolutus','c':'Constructus','d':'Determiniert'}[rest[0]]));rest=rest[1:]
        if rest:return None
    elif pos in ('P','S'):
        types=_H_PRONOUN if pos=='P' else _H_SUFFIX
        if rest and rest[0] in types:
            features.append(('Typ',types[rest[0]]));rest=rest[1:]
        # OSHB uses x in non-applicable slots, especially the person slot
        # of demonstrative/relative pronouns. Preserve the known following
        # gender and number instead of rejecting the whole code.
        if rest and rest[0]=='x' and len(rest)>1:rest=rest[1:]
        if rest and rest[0] in '123':
            features.append(('Person',rest[0]+'. Person'));rest=rest[1:]
        if rest and rest[0] in H_GENDER:
            features.append(('Genus',H_GENDER[rest[0]]));rest=rest[1:]
        if rest and rest[0] in H_NUM:
            features.append(('Numerus',H_NUM[rest[0]]));rest=rest[1:]
        if rest:return None
    elif pos=='T':
        if rest:
            if rest not in _H_PARTICLE:return None
            features.append(('Typ',_H_PARTICLE[rest]))
    elif pos=='R':
        if rest:
            if rest!='d':return None
            features.append(('Typ','Präposition mit bestimmtem Artikel'))
    elif pos in ('C','D') and rest:
        return None
    return features


def decode_hebrew(raw):
    raw=(raw or '').strip()
    fail={'recognized':False,'features':[],
          'notice':'Hebräischer Morphologie-Code derzeit nicht vollständig erkannt. Originalcode bleibt verfügbar.',
          'raw':raw}
    if not raw:return fail
    if raw[0] not in 'HA':return fail
    aramaic=raw[0]=='A'
    parts=raw[1:].split('/')
    if not 1<=len(parts)<=10:return fail
    expanded=[]
    for part in parts:
        info=_hebrew_part(part,aramaic)
        if not info:return fail
        expanded.append(info)
    if len(expanded)==1:
        features=expanded[0]
    else:
        # Preserve each affix as a component. The final part is normally the
        # headword, but no claim is made about syntax or lexical meaning.
        chain=' + '.join(part[0][1] for part in expanded)
        features=[('Wortart',chain)]
        for index,info in enumerate(expanded,1):
            if index==len(expanded):
                features.extend((f'Hauptwort: {key}',value) for key,value in info[1:])
            else:
                features.extend((f'Teil {index}: {key}',value) for key,value in info[1:])
    return {'recognized':True,'features':[{'name':k,'value':v} for k,v in features],
            'raw':raw,'scheme':'Open Scriptures Hebrew Morphology',
            'components':len(expanded)}
