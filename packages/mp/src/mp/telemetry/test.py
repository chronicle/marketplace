import traceback


def risky_division(a, b):
    # This is where the error will happen
    return a / b


def main():
    try:
        result = risky_division(10, 0)
        print(f"The result is: {result}")
    except Exception:
        print("--- An error occurred! ---")

        # Here is where we call the function
        stack_trace_string = traceback.format_exc()

        print("\n--- traceback.format_exc() returned: ---")
        print(stack_trace_string)


# Run the main function
main()
