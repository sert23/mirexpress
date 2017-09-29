#!/bin/bash
#PBS -l walltime=24:30,mem=4Gb

export PYTHONPATH=/shared/
workon dev
runPipelines $key $name $outdir $pipeline --desc $matrixDesc -i $input --iso $iso --nt $nt --dt $dt --hmTop $hmTop --hmPerc $hmPerc

