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
H_STEM={'q':'Qal','N':'Nifal','p':'Piel','P':'Pual','h':'Hifil','H':'Hofal','t':'Hitpael','o':'Polel','O':'Polal','r':'Hitpolel','m':'Poel','M':'Poal','k':'Palel','K':'Pulal','Q':'Qal Passiv','l':'Pilpel','L':'Polpal','f':'Hitpalpel','D':'Nithpael'}
H_CONJ={'p':'Perfekt (Suffixkonjugation)','q':'Perfekt (Suffixkonjugation)','i':'Imperfekt (Präfixkonjugation)','w':'Waw-konsekutiv / Wayyiqtol','h':'Kohortativ','j':'Jussiv','v':'Imperativ','r':'Partizip aktiv','s':'Partizip passiv','a':'Infinitiv absolut','c':'Infinitiv constructus'}
H_GENDER={'m':'Maskulinum','f':'Femininum','c':'Gemeinsames Genus'}
H_NUM={'s':'Singular','p':'Plural','d':'Dual'}
def decode(morph,language):
    raw=(morph or '').strip()
    if not raw:return {'recognized':False,'features':[],'notice':'Keine morphologischen Informationen angegeben.','raw':raw}
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
        # OSHB e.g. HVqp3ms, Vqp3ms, HNcmsa; slash-delimited complexes are not guessed.
        s=raw[1:] if raw.startswith('H') and len(raw)>1 else raw
        if '/' not in s and s:
            pos=s[0]
            if pos in H_POS:
                add('Wortart',H_POS[pos])
                if pos=='V' and len(s)>=3 and s[1] in H_STEM and s[2] in H_CONJ:
                    add('Stamm',H_STEM[s[1]]);add('Form',H_CONJ[s[2]])
                    rest=s[3:]
                    if rest and rest[0] in '123':add('Person',rest[0]+'. Person');rest=rest[1:]
                    if rest and rest[0] in H_GENDER:add('Genus',H_GENDER[rest[0]]);rest=rest[1:]
                    if rest and rest[0] in H_NUM:add('Numerus',H_NUM[rest[0]]);rest=rest[1:]
                    if not rest:return {'recognized':True,'features':features,'raw':raw,'scheme':'Open Scriptures Hebrew Morphology'}
                if pos in ('N','A') and len(s)>=3:
                    rest=s[1:]
                    if rest[0] in ('c','p','g'):add('Typ',{'c':'Gattungsname','p':'Eigenname','g':'Gentilizium'}[rest[0]]);rest=rest[1:]
                    if rest and rest[0] in H_GENDER:add('Genus',H_GENDER[rest[0]]);rest=rest[1:]
                    if rest and rest[0] in H_NUM:add('Numerus',H_NUM[rest[0]]);rest=rest[1:]
                    if rest and rest[0] in ('a','c','d'):add('Status',{'a':'Absolutus','c':'Constructus','d':'Determiniert'}[rest[0]]);rest=rest[1:]
                    if not rest and len(features)>1:return {'recognized':True,'features':features,'raw':raw,'scheme':'Open Scriptures Hebrew Morphology'}
    return {'recognized':False,'features':[],'notice':'Codeformat derzeit nicht sicher erkannt. Der Originalcode bleibt erhalten; es wird keine Grammatik geraten.','raw':raw}
