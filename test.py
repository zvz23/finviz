def divide_list_into_three(lst):
    n = len(lst)
    # Calculate the size of each part
    part_size = n // 3
    remainder = n % 3
    
    # Determine the indices where to split the list
    first_end = part_size + (1 if remainder > 0 else 0)
    second_end = first_end + part_size + (1 if remainder > 1 else 0)
    
    # Slice the list into three parts
    part1 = lst[:first_end]
    part2 = lst[first_end:second_end]
    part3 = lst[second_end:]
    
    return part1, part2, part3



print(divide_list_into_three(list(range(11))))