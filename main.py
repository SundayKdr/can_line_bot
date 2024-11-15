import controller


controller = controller.Controller(interface="socketcan", channel="can0",
                                   token="6334953390:AAE9kpsXKuF9LRIh50yfVb9WbA5wyrU7fP8")


def main() -> None:
    controller.start_app()


if __name__ == "__main__":
    main()
