class OrdersService:
    def handle(self, message: dict) -> None:
        print("[OrdersService]", message)
