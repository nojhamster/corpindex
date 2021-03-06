
# Cqpl_Cqpl_parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = b'\x04\x11\x00\x07\xbf\xa07V\x17\x1a\xfc\xf6\xac!\xf6D'
    
_lr_action_items = {'NUM':([13,17,],[26,29,]),'=':([9,],[22,]),'~':([9,],[23,]),'ZONE':([5,7,11,16,30,31,35,36,37,],[-20,17,-13,-17,-14,-15,-18,-19,-16,]),'|':([2,4,5,7,11,14,15,16,21,24,25,26,27,28,30,31,34,35,36,37,38,],[12,-7,-20,19,-13,12,12,19,-8,19,-4,-2,-1,-5,19,-15,-9,-18,-19,-16,-6,]),'(':([0,1,2,3,4,6,10,12,14,15,18,19,21,25,26,27,28,34,38,],[3,10,3,3,-7,10,10,3,-3,3,10,10,-8,-4,-2,-1,-5,-9,-6,]),']':([5,7,8,11,16,20,29,30,31,32,33,35,36,37,40,],[-20,-10,21,-13,-17,-23,-12,-14,-15,-11,-21,-18,-19,-16,-22,]),'?':([21,28,],[34,38,]),'GROUPE':([13,],[27,]),'[':([0,2,3,4,12,14,15,21,25,26,27,28,34,38,],[1,1,1,-7,1,-3,1,-8,-4,-2,-1,-5,-9,-6,]),'WITHIN':([2,4,14,15,21,25,26,27,28,34,38,],[13,-7,-3,13,-8,-4,-2,-1,-5,-9,-6,]),'&':([5,7,11,16,24,30,31,35,36,37,],[-20,18,-13,18,18,-14,-15,-18,-19,-16,]),'VALATT':([22,23,],[35,36,]),'!':([1,6,10,18,19,],[6,6,6,6,6,]),'ATT':([1,6,10,18,19,20,39,],[9,9,9,9,9,9,9,]),',':([5,20,32,33,35,36,40,],[-20,-23,39,-21,-18,-19,-22,]),'/':([5,7,11,16,30,31,35,36,37,],[-20,20,-13,-17,-14,-15,-18,-19,-16,]),'$end':([2,4,14,21,25,26,27,28,34,38,],[0,-7,-3,-8,-4,-2,-1,-5,-9,-6,]),')':([4,5,11,14,15,16,21,24,25,26,27,28,30,31,34,35,36,37,38,],[-7,-20,-13,-3,28,-17,-8,37,-4,-2,-1,-5,-14,-15,-9,-18,-19,-16,-6,]),'MOT':([1,6,10,18,19,20,39,],[5,5,5,5,5,5,5,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'ensmot':([0,2,3,12,14,15,25,],[2,14,15,25,14,14,14,]),'defmot':([1,6,10,18,19,],[7,16,24,30,31,]),'motmod':([1,],[8,]),'modif':([20,],[32,]),'mot':([0,2,3,12,14,15,25,],[4,4,4,4,4,4,4,]),'attval':([1,6,10,18,19,20,39,],[11,11,11,11,11,33,40,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> ensmot","S'",1,None,None,None),
  ('ensmot -> ensmot WITHIN GROUPE','ensmot',3,'p_expr_groupe','./Cqpl.py',148),
  ('ensmot -> ensmot WITHIN NUM','ensmot',3,'p_expr_groupe_num','./Cqpl.py',153),
  ('ensmot -> ensmot ensmot','ensmot',2,'p_expr','./Cqpl.py',158),
  ('ensmot -> ensmot | ensmot','ensmot',3,'p_expr_ou','./Cqpl.py',163),
  ('ensmot -> ( ensmot )','ensmot',3,'p_expr_parenthese','./Cqpl.py',168),
  ('ensmot -> ( ensmot ) ?','ensmot',4,'p_expr_parenthese_opt','./Cqpl.py',173),
  ('ensmot -> mot','ensmot',1,'p_expr_mot','./Cqpl.py',178),
  ('mot -> [ motmod ]','mot',3,'p_mot','./Cqpl.py',185),
  ('mot -> [ motmod ] ?','mot',4,'p_mot','./Cqpl.py',186),
  ('motmod -> defmot','motmod',1,'p_motmod','./Cqpl.py',195),
  ('motmod -> defmot / modif','motmod',3,'p_motmod','./Cqpl.py',196),
  ('motmod -> defmot ZONE NUM','motmod',3,'p_motmod','./Cqpl.py',197),
  ('defmot -> attval','defmot',1,'p_defmot','./Cqpl.py',209),
  ('defmot -> defmot & defmot','defmot',3,'p_defmot','./Cqpl.py',210),
  ('defmot -> defmot | defmot','defmot',3,'p_defmot','./Cqpl.py',211),
  ('defmot -> ( defmot )','defmot',3,'p_defmot','./Cqpl.py',212),
  ('defmot -> ! defmot','defmot',2,'p_defmot','./Cqpl.py',213),
  ('attval -> ATT = VALATT','attval',3,'p_attval','./Cqpl.py',230),
  ('attval -> ATT ~ VALATT','attval',3,'p_attval','./Cqpl.py',231),
  ('attval -> MOT','attval',1,'p_attval','./Cqpl.py',232),
  ('modif -> attval','modif',1,'p_modif','./Cqpl.py',244),
  ('modif -> modif , attval','modif',3,'p_modif','./Cqpl.py',245),
  ('modif -> <empty>','modif',0,'p_modif','./Cqpl.py',246),
]
