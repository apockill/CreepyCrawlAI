def clamp(val, lower, upper):
    """Performant clamp function"""
    return lower if val < lower else upper if val > upper else val
