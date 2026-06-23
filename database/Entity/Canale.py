from dataclasses import dataclass

@dataclass
class Canale:
    canale_id: str
    nome_canale: str
    id_affiliato: str
    codice_licenza: str
    amazon_tag: str
    venditoreamazon_tag: str
    venditore_tag: str
    preorder_tag: str
    prime_tag: str
    offertaexcl_tag: str
