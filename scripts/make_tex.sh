#!/usr/bin/env bash

if [ "$1" == "-h" -o "$1" == "--help" ]
then
	echo 'Usage: $PDF_VIEWER $('$0' [preamble] < my_tex_table.tex)' >&2
	echo >&2
	echo 'Builds a LaTeX document from stdin:' >&2
	echo '- accepts TeX content on stdin;' >&2
	echo '- wraps it in the headers and footers for a LaTeX document;' >&2
	echo '- compiles it to PDF (or DVI/PS if necessary) in a temporary directory.' >&2
	echo 'The output path will be echoed to stdout.' >&2
	echo 'Additional preamble content (\usepackage{..}, etc.) may be provided as command-line arguments.' >&2
	exit 1
fi

tmpdir="$(mktemp -d -t $(basename $0))" || exit 1
path="$tmpdir/doc"
cd "$tmpdir"

echo '\documentclass{article}\usepackage{fullpage}'"$@"'\begin{document}' > "$path.tex"
cat >> "$path.tex"
echo '\end{document}' >> "$path.tex"

if [ -x "$(which pdflatex)" ]
then
	pdflatex $path >&2 && out="$path.pdf"
else
	latex $path >&2 && out="$path.dvi"
	dvips $path >&2 && out="$path.ps"
	ps2pdf $path.ps $path.pdf >&2 && out="$path.pdf"
fi

if [ -e "$out" ]
then
	echo 'Output in' >&2
	echo $out
fi
