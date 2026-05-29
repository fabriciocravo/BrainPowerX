function skip = skip_outcome(dataset, outcome)

    switch dataset

        case 'hbn'

            if strcmp(outcome,'test1')
                skip = true;
            else
                skip = false;
            endif

        otherwise
          skip = false;

    endswitch

end


