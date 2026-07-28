function outcome = map_task_to_outcome(dataset, task)
    switch dataset

        case 'hbn'
          switch task
              case 'test2',  outcome = 'social_responsiveness';
              case 'test3',  outcome = 'cognitive_flexibility';
              case 'test4',  outcome = 'inhibitory_control';
              case 'test5',  outcome = 'working_memory';
              case 'test6',  outcome = 'processing_speed';
              otherwise,     outcome = task;
          end

        case 'abcd'
            switch task
                % Category 1: Demographics & Basic Measures
                case 'test1',  outcome = 'sex';
                case 'test2',  outcome = 'wisc_v_iq';
                case 'test3',  outcome = 'age';
                case 'test4',  outcome = 'bmi_z';
                % Category 2: CBCL Baseline
                case 'test5',  outcome = 'cbcl_internalizing';
                case 'test6',  outcome = 'cbcl_externalizing';
                case 'test7',  outcome = 'cbcl_aggressive';
                case 'test8',  outcome = 'cbcl_rule_breaking';
                case 'test9',  outcome = 'cbcl_attention';
                case 'test10', outcome = 'cbcl_thought';
                case 'test11', outcome = 'cbcl_social';
                case 'test12', outcome = 'cbcl_somatic';
                case 'test13', outcome = 'cbcl_withdrawn';
                case 'test14', outcome = 'cbcl_anx_dep';
                % Category 3: UPPS Impulsivity
                case 'test15', outcome = 'upps_lack_planning';
                case 'test16', outcome = 'upps_lack_perseverance';
                case 'test17', outcome = 'upps_sensation_seeking';
                case 'test18', outcome = 'upps_neg_urgency';
                case 'test19', outcome = 'upps_pos_urgency';
                % Category 4: Substance Use
                case 'test20', outcome = 'substance_use';
                % Category 5: CBCL Follow-up 1
                case 'test21', outcome = 'cbcl_internalizing_fu1';
                case 'test22', outcome = 'cbcl_externalizing_fu1';
                case 'test23', outcome = 'cbcl_aggressive_fu1';
                case 'test24', outcome = 'cbcl_rule_breaking_fu1';
                case 'test25', outcome = 'cbcl_attention_fu1';
                case 'test26', outcome = 'cbcl_thought_fu1';
                case 'test27', outcome = 'cbcl_social_fu1';
                case 'test28', outcome = 'cbcl_somatic_fu1';
                case 'test29', outcome = 'cbcl_withdrawn_fu1';
                case 'test30', outcome = 'cbcl_anx_dep_fu1';
                % Category 6: CBCL Change Scores
                case 'test31', outcome = 'cbcl_internalizing_delta';
                case 'test32', outcome = 'cbcl_externalizing_delta';
                case 'test33', outcome = 'cbcl_aggressive_delta';
                case 'test34', outcome = 'cbcl_rule_breaking_delta';
                case 'test35', outcome = 'cbcl_attention_delta';
                case 'test36', outcome = 'cbcl_thought_delta';
                case 'test37', outcome = 'cbcl_social_delta';
                case 'test38', outcome = 'cbcl_somatic_delta';
                case 'test39', outcome = 'cbcl_withdrawn_delta';
                case 'test40', outcome = 'cbcl_anx_dep_delta';
                otherwise,     outcome = task;
            end

        case 'slim'
            
            switch task
                case 'test1',  outcome = 'state_anxiety';
                case 'test2',  outcome = 'sex';
            end
        otherwise
            outcome = task;
    end
end
