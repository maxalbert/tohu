def print_generated_sequence(g, num, *, sep=", "):
    """
    Helper function which prints a sequence of `num` items
    produced by the random generator `g`.
    """

    elems = [str(next(g)) for _ in range(num)]
    sep_initial = "\n" if sep == "\n" else " "
    print("Generated sequence:{}{}".format(sep_initial, sep.join(elems)))
