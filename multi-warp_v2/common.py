
FEATURE_LENGTH= 25
CONTEXT_LENGTH= 20
OUT_LATENCY= 3
BUFFER_LENGTH= 2

BLOCK=0
S_MEM=1
G_MEM=2


col_name_file=['dataset','kid', 'uid', 'exe_time', 'ibuff_time', 'issued_time', 'latency',
       'src_regs', 'dst_regs', 'isload', 'isstore', 'memwidth', 'op',
       'sp_op', 'op_pipe', 'mem_op', 'oprd_type', 'initiation_interval',
       'active_inst', 'isatomic', 'cache_status', 'reconvergence',
       'bar_type', 'red_type', 'bar_count', 'cache_op', 'instr', 'wb_id',
       'buffer_order', 'fetch_lat', 'issue_lat', 'execution_lat']




#all=[instr_map.get(instr,instr) for instr in frames['inst'].values]
#no_integers = [x for x in all if not isinstance(x, int)]
#set(no_integers)
#Keymax = max(instr_map, key= lambda x: instr_map[x])
#max= instr_map.get(Keymax)
