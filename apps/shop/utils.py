def colour_size_filter_products(products_original, sizes, colours):
    products = products_original
    sized_products = None
    coloured_products = None

    if len(sizes) > 0:
        sized_products = products_original.exclude(sizes=None)
        if not "ALL" in sizes:  # incase of an ALL option
            sized_products = products_original.filter(sizes__value__in=sizes)
        products = sized_products

    if len(colours) > 0:
        coloured_products = products_original.exclude(colours=None)
        if not "ALL" in colours:
            coloured_products = products_original.filter(colours__value__in=colours)
        products = coloured_products

    if sized_products and coloured_products:
        products = sized_products | coloured_products
    return products.distinct()
