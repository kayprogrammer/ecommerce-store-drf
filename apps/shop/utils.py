def color_size_filter_products(products_original, sizes, colors):
    products = products_original
    sized_products = None
    colored_products = None

    if len(sizes) > 0:
        sized_products = products_original.exclude(sizes=None)
        if not "ALL" in sizes:  # incase of an ALL option
            sized_products = products_original.filter(sizes__value__in=sizes)
        products = sized_products

    if len(colors) > 0:
        colored_products = products_original.exclude(colors=None)
        if not "ALL" in colors:
            colored_products = products_original.filter(colors__value__in=colors)
        products = colored_products

    if sized_products and colored_products:
        products = sized_products | colored_products
    return products.distinct()
