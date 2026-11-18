from csp_solver import change_rules
from keypad import KeypadController

def main():
    keypad=KeypadController()
    old=keypad.solve_current()
    print('Original:',old.to_dict())
    assert keypad.submit(old.code,old.revision)
    assert not keypad.can_unlock(False)
    assert keypad.can_unlock(True)
    keypad.update_rules(change_rules(keypad.puzzle,total=21))
    assert not keypad.can_unlock(True)
    assert not keypad.submit(old.code,old.revision)
    new=keypad.solve_current()
    assert keypad.submit(new.code,new.revision)
    assert keypad.can_unlock(True)
    print('Changed:',new.to_dict())
    keypad.update_rules(change_rules(keypad.puzzle,total=100))
    result=keypad.solve_current()
    assert result.status=='unsatisfiable'
    assert not keypad.submit(result.code,result.revision)
    assert not keypad.can_unlock(True)
    print('Impossible puzzle safely kept locked. All integration assertions passed.')

if __name__=='__main__':
    main()
