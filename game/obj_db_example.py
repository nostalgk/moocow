import evennia

# The simplest way to get/set Attributes is to use the .db shortcut.
# This allows for setting and getting Attributes that lack a category (having category None)

# Trying to access a non-existing Attribute will never lead to an AttributeError.
# Instead you will get None back. The special .db.all will return a list of all Attributes on the object.
# You can replace this with your own "Attribute all" if you want,
# it will replace the default all functionality until you delete it again.

"""
If you don’t specify a category, the Attribute’s category will be None and can thus also be found via .db. 

None is considered a category of its own, so you won’t find None-category Attributes mixed with Attributes having categories.

Here are the methods of the AttributeHandler. See the AttributeHandler API for more details.

    has(...) - this checks if the object has an Attribute with this key. 
    This is equivalent to doing obj.db.attrname except you can also check for a specific `category.

    get(...) - this retrieves the given Attribute. 
    You can also provide a default value to return if the Attribute is not defined (instead of None). 
    By supplying an accessing_object to the call one can also make sure to check permissions before modifying anything. 
    The raise_exception kwarg allows you to raise an AttributeError instead of returning None when you access a non-existing Attribute. 
    The strattr kwarg tells the system to store the Attribute as a raw string rather than to pickle it. 
    While an optimization this should usually not be used unless the Attribute is used for some particular, limited purpose.

    add(...) - this adds a new Attribute to the object. 
    An optional lockstring can be supplied here to restrict future access and also the call itself may be checked against locks.

    remove(...) - Remove the given Attribute. 
    This can optionally be made to check for permission before performing the deletion. 
    clear(...) - removes all Attributes from object.

    all(category=None) - returns all Attributes (of the given category) attached to this object.
"""

obj = evennia.create_object(key="Foo")

obj.db.foo1 = 1234
obj.db.foo2 = [1, 2, 3, 4]
obj.db.weapon = "sword"
obj.db.self_reference = obj  # stores a reference to the obj

# (let's assume a rose exists in-game)
rose = evennia.search_object(key="rose")[0]  # returns a list, grab 0th element
rose.db.has_thorns = True

# retrieving
val1 = obj.db.foo1
val2 = obj.db.foo2
weap = obj.db.weapon
myself = obj.db.self_reference  # retrieve reference from db, get object back

is_ouch = rose.db.has_thorns

# this will return None, not AttributeError!
not_found = obj.db.jiwjpowiwwerw

# returns all Attributes on the object
obj.db.all

# delete an Attribute
del obj.db.foo2

# you can give space-separated Attribute-names (can't do that with .db)

is_ouch = rose.attributes.get("has_thorns")

obj.attributes.add("helmet", "Knight's helmet")
helmet = obj.attributes.get("helmet")

# you can give space-separated Attribute-names (can't do that with .db)
obj.attributes.add("my game log", "long text about ...")

# store (let's say we have gold_necklace and ringmail_armor from before)
obj.attributes.add("neck", "gold_necklace", category="clothing")
obj.attributes.add("neck", "ringmail_armor", category="armor")

# retrieve later - we'll get back gold_necklace and ringmail_armor
neck_clothing = obj.attributes.get("neck", category="clothing")
neck_armor = obj.attributes.get("neck", category="armor")

try:
    # raise error if Attribute foo does not exist
    val = obj.attributes.get("foo", raise_exception=True)
except AttributeError:
    pass
# ...

# return default value if foo2 doesn't exist
val2 = obj.attributes.get("foo2", default=[1, 2, 3, "bar"])

# delete foo if it exists (will silently fail if unset, unless
# raise_exception is set)
obj.attributes.remove("foo")

# view all clothes on obj
all_clothes = obj.attributes.all(category="clothes")
