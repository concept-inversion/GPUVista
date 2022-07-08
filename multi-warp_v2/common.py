
FEATURE_LENGTH= 25
CONTEXT_LENGTH= 20
OUT_LATENCY= 3
BUFFER_LENGTH= 2

BLOCK=0
SMEM=1
GMEM=2

TRUTH=0
PREDICTION=1

BLOCK_CONTEXT= 22
SMEM_CONTEXT= 10
GMEM_CONTEXT= 50
#printf("%d,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%d,%d,%d,%u,%u,%d,%d,%d,%d,%#x,%d,%s,%llu,%u,%llu \n",1,m_kernel->get_uid(),m_sid,inst.get_schd_id(),inst.warp_id(),inst.get_uid(), inst.latency,inst.src_regs,inst.dst_regs,inst.is_load(),inst.is_store(), inst.data_size, inst.op, inst.sp_op, inst.op_pipe, inst.mem_op,inst.oprnd_type, inst.initiation_interval, inst.get_active_mask().count(), inst.isatomic(), inst.get_cache_status(), (int)inst.bar_type, (int)inst.red_type, (int)inst.bar_count, (int)inst.cache_op, inst.pc,inst.reconvergence_pc, inst.inst_name, inst.fetch_cycle + m_gpu->gpu_tot_sim_cycle, inst.get_issue_cycle(),m_gpu->gpu_sim_cycle + m_gpu->gpu_tot_sim_cycle);



col_name= ['kid', 'core', 'sch_id', 'warp_id', 'uid', 'latency', 'src_regs',
               'dst_regs', 'isload', 'isstore', 'memwidth', 'op', 'sp_op', 'op_pipe',
                      'mem_op', 'oprd_type', 'initiation_interval', 'active_inst', 'isatomic',
                             'cache_status', 'bar_type', 'red_type', 'bar_count', 'cache_op','space','pc',
                                    'reconvergence', 'instr', 'fetch_cycle', 'issue_cycle', 'wb_cycle']


block_features = ['src_regs',
               'dst_regs', 'isload', 'isstore', 'memwidth', 'op', 'sp_op', 'op_pipe',
                      'mem_op', 'oprd_type', 'initiation_interval', 'active_inst', 'isatomic',
                             'cache_status', 'bar_type', 'red_type', 'bar_count', 'cache_op','space','instr']

smem_features= ['isload', 'isstore', 'memwidth','bar_count','space','instr']

gmem_features= ['isload', 'isstore', 'memwidth','bar_count','space','instr']

inst_id= ['kid', 'core', 'sch_id', 'warp_id', 'uid', 'pc', 'reconvergence']
truth_f= ['fetch_cycle', 'issue_cycle', 'wb_cycle']

unique_elements= ['latency','src_regs','dst_regs','isload','isstore','memwidth','op','sp_op','op_pipe', 'mem_op','oprd_type'
        ,'initiation_interval','active_inst','isatomic','cache_status','bar_type','red_type','bar_count','cache_op','instr']



BLOCK_FEATURE= len(block_features) 
SMEM_FEATURE= len(smem_features)
GMEM_FEATURE= len(gmem_features)

BLOCK_INPUT_SIZE= BLOCK_FEATURE*BLOCK_CONTEXT 
SMEM_INPUT_SIZE= SMEM_FEATURE*SMEM_CONTEXT
GMEM_INPUT_SIZE= GMEM_FEATURE*GMEM_CONTEXT

def mapper(j_file, opcode):
    op_int= int(j_file.get(opcode))
    return op_int


#all=[instr_map.get(instr,instr) for instr in frames['inst'].values]
#no_integers = [x for x in all if not isinstance(x, int)]
#set(no_integers)
#Keymax = max(instr_map, key= lambda x: instr_map[x])
#max= instr_map.get(Keymax)
