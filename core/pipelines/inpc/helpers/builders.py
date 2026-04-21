def idE(location_type: str, category_id: int = 1) -> str:
    match location_type:
        case "City":
            if not (1 <= category_id <= 55):
                raise ValueError("category_id out of range: should be between (1..55)")
            return f"1120017000600{category_id:02d}0"
        case "Entity":
            if not (1 <= category_id <= 32):
                raise ValueError("category_id out of range: should be between (1..32)")
            return f"1120017000700{category_id:02d}0"
        case "National":
            return "112001700030"
        case _:
            raise ValueError(f"invalid location_type: {location_type}. Use 'City', 'Entity' or 'National'")
