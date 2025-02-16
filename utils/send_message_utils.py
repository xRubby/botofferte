def venduto_e_spedito(venditore: str, spedito_Amazon: bool):
    if("Amazon" in venditore and spedito_Amazon):
        return "Venduto e spedito da Amazon"
    elif("Amazon" not in venditore and spedito_Amazon):
        return f"Venduto da {venditore} e spedito da Amazon"
    
    return f"Venduto e spedito da {venditore}"