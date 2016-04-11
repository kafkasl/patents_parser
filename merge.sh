if [ $# -eq 2 ]; then

threads=$1
name=$2

target="patent_assignments_$1_$2"
mkdir -p $target
for file in results_$1*$2/*csv; do
	cp $file $target
done

else
   echo "Invalid # of arguments: threads name"
fi
