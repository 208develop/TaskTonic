from rfc3986.validators import host_is_valid

from TaskTonic.internals import Store

s = Store()

s['test'] = 1

s['list/#'] = 'name1' # list root
s['list/./a'] = 1
s['list/./b'] = 2

s['list1/#/name'] = 'name2'
s['list1/./a'] = 1
s['list1/./b'] = 2

i = s['list2'].append()
i.v = 'name3'
i['a'] = 1
i['b'] = 2

i = s['list2'].append()
i.v = 'name4'
i['a'] = 3
ii = i['b/c']
ii.v = 4

s['list2'].append().v = 'name5'

print(i)
l = s.at('list/#')
l['l'] = 10

_session = s.at('session')
store_session = _session.append()
store_session['s'] = 's1'

print("s:"+s.dumps())

print("i:"+i.dumps())
print("i.list_root:"+i.list_root.dumps())
print("i.parent:"+i.parent.dumps())

print("ii:"+ii.dumps())
print("ii.list_root:"+ii.list_root.dumps())
print("ii.list:"+ii.list_root.parent.dumps())

d = i.list_root.pop()
print(f"d: {d}")
print(s.dumps())



i = s['list3'].append()
i['name'].v = 'name31'
i['a'] = 3
ii = i['b/c']
ii.v = 4
i = s['list3'].append()
i['name'].v = 'name32'
i['a'] = 5
ii = i['b/c']
ii.v = 6

print("i:" + i.dumps())
print("i.list_root:" + i.list_root.dumps())
print("i.parent:" + i.parent.dumps())

print("ii:" + ii.dumps())
print("ii.list_root:" + ii.list_root.dumps())
print("ii.list:" + ii.list_root.parent.dumps())

print(s.dumps())
p = i.pop()
print(p)
print(s.dumps())

c = s.get_children_keys(path='')
print(c)
c = s.get_children_keys(path='list2')
print(c)

ic = s['list2'].children()
for c in ic:
    print(c)
    print(c.dumps())

print (s.dump())