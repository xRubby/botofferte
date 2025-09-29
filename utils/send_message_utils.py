from database.DAO.CanaleDAO import CanaleDAO

def venduto_e_spedito(venditore: str, spedito_Amazon: bool, channel_id: str = None) -> str:

    with CanaleDAO() as canale_dao:
        canale = canale_dao.get(channel_id)

    if canale is not None:
        if("Amazon" in venditore and spedito_Amazon):
            return canale.amazon_tag if canale.amazon_tag else "Venduto e spedito da Amazon"
        elif("Amazon" not in venditore and spedito_Amazon):
            return canale.venditoreamazon_tag.replace("{venditore}", venditore) if canale.venditoreamazon_tag else f"Venduto da {venditore} e spedito da Amazon"
        return canale.venditore_tag.replace("{venditore}", venditore) if canale.venditore_tag else f"Venduto e spedito da {venditore}"
    else:
        if("Amazon" in venditore and spedito_Amazon):
            return "Venduto e spedito da Amazon"
        elif("Amazon" not in venditore and spedito_Amazon):
            return f"Venduto da {venditore} e spedito da Amazon"
        return f"Venduto e spedito da {venditore}"


    