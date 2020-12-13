import copy, re

def convert_units_ing(quantity, unit):
    """
    Pass in a number and a quantity in metric units
    Returns a number and quantity in (American) imperial units
    """
    try:
        quantity = str(quantity)
    except:
        raise TypeError("quantity cannot be coerced into a string")

    try:
        unit = str(unit)
    except:
        raise TypeError("unit cannot be coerced into a string")

    # Dict is in the format:
    # key : (ratio, translated_key)
    # Constants are not needed
    # because temperatures are not passed in
    unit_conversion = {
        'g': (0.00220462, 'lb'),
        'gr': (0.00220462, 'lb'),
        'grammi': (0.00220462, 'lb'),
        'kg': (2.205, 'lb'),
        'l': (33.8140227, 'fl oz'),
        'litri': (33.8140227, 'fl oz'),
        'ml': (33.8140227 / 1000, 'fl oz'),
        'millilitri': (33.8140227 / 1000, 'fl oz')
    }
    unit_lower = unit.lower()
    if unit_lower in unit_conversion:
        # The quantity can sometimes contain , instead of .
        # because decimals are written with a comma
        quantity = quantity.replace(',', '.')
        # There is no need for a try/except block because
        # it will be of the proper format if it has gotten this far
        con_q = (round(unit_conversion[unit_lower][0] * float(quantity), 2))
        con_u = unit_conversion[unit_lower][1]
        # Sometimes units will be something like .14 lb
        # So they will be converted to oz if they are small enough
        # Or fl oz to cups/quarts if they're large enough
        con_q, con_u = simplify_units(con_q, con_u)
        return con_q, con_u
    else:
        try:
            quantity = round(float(quantity), 2)
        finally:
            return (quantity, unit)

def convert_units_prep(prep):
    """
    Takes a string, parses it for metric units and converts both them and the quantities into imperial units and quantities
    """
    # We'll make a copy so we don't have any side effects
    # Because we'll be doing some replacing if we have a hit
    return_string = copy.deepcopy(prep)

    # this dictionary is of the format:
    # key: (scalar, constant, unit)
    # N.B. Both temperatures and lengths are here
    unit_conversions = {
        'g': (0.00220462, 0, 'lb'),
        'gr': (0.00220462, 0, 'lb'),
        'grammi': (0.00220462, 0, 'lb'),
        'kg': (2.205, 0, 'lb'),
        'l': (33.814, 0, 'fl oz'),
        'litri': (33.814, 0, 'fl oz'),
        'ml': (33.814 / 1000, 0, 'fl oz'),
        'millilitri': (33.814 / 1000, 0, 'fl oz'),
        '°': (1.8, 32, '°'),
        'gradi': (1.8, 32, 'gradi'),
        'c': (1.8, 32, 'F'),
        'cm': (0.3937, 0, 'inches'),
        'mm': (0.03937, 0, 'inches'),
        'm': (39.37, 0, 'inches')
    }
    # When there is a unit, it comes in one of twoformats:
    # 1. quantityunit - i.e. 300g
    # 2. quantity(any of , . / - x)fraction(space)unit - i.e. 1,5 l
    # Regex 3 is so the expression correctly classifies something
    # as the former and the latter as the latter
    # i.e. 1,5l isn't treated as 1, as not a unit and 5l
    # group(1) will always be the quantity, group(2) always the unit
    regex = ['(\d+)([a-zA-Z°]+)', '(\d+[,\.]?\d*[\/\-x]\d+[,\.]?\d*)[\s]?([a-zA-Z°]+)', '(\d+[,\.\/\-x]\d+)[\s]?([a-zA-Z°]+)', '[^,\./-x](\d+)[\s]?([a-zA-Z°]+)']
    
    for ex in regex:
        match = re.findall(ex, return_string)
        # it's possible that there are multiple unit conversions in one line
        # i.e. 'mettere 1,5 l di crema con 300g di pollo'
        if len(match) > 0:
            # looping through every match
            for group in match:
                # we will get lots of false positives
                # they'll get ignored if they're not
                # of the appropriate form
                if group[1].lower() in unit_conversions:

                    # The unit is just the converted unit name and the simplest to replace
                    conv_unit = unit_conversions[group[1]][2]
                    
                    # Regex[1], because of the , . - needs special treatment
                    if ex == regex[1] or ex == regex[2]:
                        # We are doing the same replacement that we did above
                        # replacing , with . so it can be converted to a float
                        amount_punctuation_replaced = group[0].replace(',', '.')
                        try:
                            # This is the simplest case: that it's something like 1,5 (now 1.5)
                            # So we can just make it into a float
                            amount = float(amount_punctuation_replaced)
                            # The converted quantity is equal to the float times the scalar plus the constant
                            conv_amount = round((amount * unit_conversions[group[1]][0]) + unit_conversions[group[1]][1], 2)
                            # We are passing it to the same function to simplify it so we don't have 0.14 lb
                            # Unfortunately we have to repeat it once for every different situation
                            conv_amount, conv_unit = simplify_units(conv_amount, conv_unit)
                        # Except occurs if it's not a , but something else
                        # such as - as in 2-3
                        except:
                            # Therefore we are preserving the two digits as separate entities
                            # But otherwise doing the same action
                            # This regex should capture both 1-2 and 1.2-5.2
                            digits = re.findall('(\d+[,\.]?\d*)(\D)(\d+[,\.]?\d*)', amount_punctuation_replaced)[0]
                            first_digit = round((float(digits[0]) * unit_conversions[group[1]][0]) + unit_conversions[group[1]][1], 2)
                            second_digit = round((float(digits[2]) * unit_conversions[group[1]][0]) + unit_conversions[group[1]][1], 2)
                            temp_first_digit, first_conv_unit = simplify_units(first_digit, conv_unit)
                            temp_second_digit, second_conv_unit = simplify_units(second_digit, conv_unit)
                            # In the rare circumstance that simplify_units will give different units
                            # for a range, we ignore the converison but must dot zero it manually
                            # because simplify_units does it usually
                            if first_conv_unit == second_conv_unit:
                                first_digit = temp_first_digit
                                second_digit = temp_second_digit
                                conv_unit = first_conv_unit # Whichever of the two
                            else:
                                if float_dot_zero(first_digit):
                                    first_digit = int(first_digit)
                                if float_dot_zero(second_digit):
                                    second_digit = int(second_digit)
                            conv_amount = f"{first_digit}{digits[1]}{second_digit}"
                            # In this case, we are giving the
                            # average of the numbers; this could be improved
                    else:
                        amount = float(group[0])
                        conv_amount = round((amount * unit_conversions[group[1]][0]) + unit_conversions[group[1]][1], 2)
                        conv_amount, conv_unit = simplify_units(conv_amount, conv_unit)
                    # This was done to keep the code DRY, but regex[1] and [2] have spaces
                    # that are needed for the matching

                    if ex != regex[0]:
                        replaced_seq = f"{group[0]} {group[1]}"
                        replacing_seq = f"{conv_amount} {conv_unit}"
                    else:
                        replaced_seq = f"{group[0]}{group[1]}"
                        replacing_seq = f"{conv_amount}{conv_unit}"

                    # Every iteration, we're replacing the converted
                    return_string = return_string.replace(replaced_seq, replacing_seq)

                    if return_string.find("° C "):
                        return_string = return_string.replace("° C ", "° F ")
    return return_string

def simplify_units(quantity, unit, change_unit = True):
    """
    Takes a quantity and unit in imperial units and if it is within certain tolerances, changes it to a more convenient quantity
    """
    return_quantity = quantity
    return_unit = unit

    # A large area for improvement is to do rounding based off of the units
    # For example: 1.07lb should really be 1 or 1.2 cups should really be 1
    if unit == 'inches' and quantity >= 12:
        # Convert any quantity over 12 inches to feet and inches
        feet = quantity // 12
        inches = quantity % 12
        return_quantity = f"{feet}'"
        return_unit = 'feet'
        if inches > 0:
            return_quantity += f"{inches}''"
            return_unit += ' and inches'
    elif unit == 'fl oz' and quantity >= 8:
        # Confort to quart/cup if the quantity is > 32 or > 8
        if quantity >= 32:
            return_quantity= round(quantity/32, 2)
            return_unit = 'quart'
        else:
            return_quantity = round(quantity/8, 2)
            return_unit = 'cup'
    elif unit == 'lb' and quantity < 1:
        # Convert to oz if quantity is less than a pound
        return_quantity = 16 * quantity
        return_unit = 'oz'
    if float_dot_zero(return_quantity):
        return_quantity = int(return_quantity)
    return return_quantity, return_unit

def float_dot_zero(qt):
    """Returns true if a float ends in .0. All other situations return false"""
    if isinstance(qt, float):
        return str(qt).endswith('.0')
    else: return False