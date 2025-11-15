import traceback


def exc_to_str(e: Exception) -> str:
    tb_list = traceback.format_exception(type(e), e, e.__traceback__)
    return "".join(tb_list)


__all__ = ["exc_to_str"]
