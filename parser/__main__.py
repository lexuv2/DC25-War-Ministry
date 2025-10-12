import fitz


def main() -> None:
    input_pdf = "test/pdf/basic-sample.pdf"
    output_txt = "output.txt"

    doc = fitz.open(input_pdf)
    with open(output_txt, "w", encoding="utf-8") as f:
        for i, page in enumerate(doc, start=1):
            f.write(f"--- Page {i} ---\n")
            f.write(page.get_text())


if __name__ == "__main__":
    main()
