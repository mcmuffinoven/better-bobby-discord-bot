# If user first time joining this voice channel
def joined_vc(before, after) -> bool:
   return (before is None and after is not None)

def switched_vc(before, after) -> bool:
   return before is not None and after is not None and before != after

def left_vc(before, after):
   return before is not None and after is None

def vc_empty(vc):
   return len(vc.members) == 0