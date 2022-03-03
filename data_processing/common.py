
FEATURE_LENGTH= 25
CONTEXT_LENGTH= 20
OUT_LATENCY= 3
BUFFER_LENGTH= 2


col_name_processed=['kid', 'uid', 'exe_time', 'ibuff_time', 'issued_time', 'latency',
       'src_regs', 'dst_regs', 'isload', 'isstore', 'memwidth', 'op',
       'sp_op', 'op_pipe', 'mem_op', 'oprd_type', 'initiation_interval',
       'active_inst', 'isatomic', 'cache_status', 'reconvergence',
       'bar_type', 'red_type', 'bar_count', 'cache_op', 'instr', 'wb_id',
       'buffer_order', 'fetch_lat', 'issue_lat', 'execution_lat']

col_name_file= ['flag','kid', 'uid', 'core', 'warp', 'exe_time', 'inst', 'ibuff_time', 'issued_time', 'latency', 'src_regs', 'dst_regs', 'isload', 'isstore', 'memwidth', 'op', 'sp_op', 'op_pipe', 'mem_op', 'oprd_type', 'initiation_interval',
     'active_inst','isatomic','cache_status','reconvergence','pc','bar_type','red_type','bar_count','cache_op']


train_cols= ['kid', 'uid', 'latency',
       'src_regs', 'dst_regs', 'isload', 'isstore', 'memwidth', 'op',
       'sp_op', 'op_pipe', 'mem_op', 'oprd_type', 'initiation_interval',
       'active_inst', 'isatomic', 'cache_status', 'reconvergence',
       'bar_type', 'red_type', 'bar_count', 'cache_op', 'instr', 'wb_id',
       'buffer_order', 'fetch_lat', 'issue_lat', 'execution_lat']


train_cols_final= ['latency',
       'src_regs', 'dst_regs', 'isload', 'isstore', 'memwidth', 'op',
       'sp_op', 'op_pipe', 'mem_op', 'oprd_type', 'initiation_interval',
       'active_inst', 'isatomic', 'cache_status', 'reconvergence',
       'bar_type', 'red_type', 'bar_count', 'cache_op', 'instr', 'wb_id',
       'buffer_order', 'fetch_lat', 'issue_lat', 'execution_lat']

drop_before_train= set(train_cols)-set(train_cols_final)
INPUT_DIMENSION= (len(train_cols_final)+OUT_LATENCY)*CONTEXT_LENGTH

#[instr_map.get(instr,instr) for instr in frames['inst'].values]
instr_map= {'.ATOMG.E.ADD.STRONG.GPU': 0, '.ATOMG.E.EXCH.STRONG.GPU': 1, 
'.ATOMG.E.MIN.S32.STRONG.GPU': 2, '.ATOMS.ADD': 3, 
'.BAR.SYNC': 4, '.BMOV.32.CLEAR': 5, '.BRA': 6, '.BSSY': 7, '.BSYNC': 8, 
'.CALL.REL.NOINC': 9, '.CS2R': 10, '.DEPBAR.LE': 11, '.EXIT': 12, 
'.F2I.FLOOR.NTZ': 13, '.F2I.FTZ.U32.TRUNC.NTZ': 14, '.F2I.U32.TRUNC.NTZ': 15,
 '.FADD': 16, '.FADD.FTZ': 17, '.FCHK': 18, '.FFMA': 19, '.FFMA.FTZ': 20, 
 '.FMUL': 21, '.FMUL.D4': 22, '.FMUL.FTZ': 23, '.FSEL': 24, '.FSETP.GEU.AND': 25, 
 '.FSETP.NEU.AND': 26, '.I2F': 27, '.I2F.U32': 28, '.I2F.U32.RP': 29, '.IABS': 30, '.IADD3': 31,
  '.IADD3.X': 32, '.IMAD': 33, '.IMAD.IADD': 34, '.IMAD.MOV': 35, '.IMAD.MOV.U32': 36, 
  '.IMAD.SHL.U32': 37, '.IMAD.WIDE': 38, '.IMAD.WIDE.U32': 39, '.IMAD.X': 40, '.ISETP.EQ.U32.AND': 41, 
  '.ISETP.GE.AND': 42, '.ISETP.GE.U32.AND': 43, '.ISETP.GT.AND': 44, '.ISETP.GT.U32.AND': 45, '.ISETP.LT.AND': 46, '.ISETP.LT.OR': 47,
   '.ISETP.LT.U32.AND': 48, '.ISETP.NE.AND': 49, '.ISETP.NE.U32.AND': 50, '.LDC': 51,
    '.LDG.E.STRONG.GPU': 52, '.LDG.E.SYS': 53, '.LDG.E.U16.SYS': 54, '.LDS.U': 55, 
    '.LDS.U.128': 56, '.LDS.U.64': 57, '.LDS.U.U16': 58, '.LEA': 59, '.LEA.HI': 60, '.LEA.HI.SX32': 61, '.LEA.HI.X': 62, '.LEA.HI.X.SX32': 63, '.LOP3.LUT': 64, '.MOV': 65, '.MUFU.RCP': 66, '.MUFU.RSQ': 67, '.NOP': 68, '.PLOP3.LUT': 69, '.RED.E.MAX.STRONG.GPU': 70, '.RED.E.MIN.STRONG.GPU': 71, '.RET.REL.NODEC': 72, '.S2R': 73, '.SEL': 74, '.SGXT': 75, '.SGXT.U32': 76, '.SHF.L.U32': 77, '.SHF.R.S32.HI': 78, '.SHF.R.U32.HI': 79, '.SHFL.IDX': 80, '.ST.E.SYS': 81, '.STG.E.64.SYS': 82, '.STG.E.SYS': 83, '.STS': 84, '.STS.64': 85, '.STS.U16': 86, '.TEX.SCR.LL': 87, 
'.TLD.SCR.LZ': 88, '.VOTE.ALL': 89, '.IMAD.U32':90,'.ISETP.EQ.AND':91,'.F2F.F64.F32':92,
'.DMUL':93,'.F2F.F32.F64':94, '.DFMA':95, '.DADD':96, 'MUFU.RCP64H':97, '.FSETP.GT.AND':98,
'.MUFU.RCP64H':99,'.LDG.E.U8.SYS':100, '.STG.E.U8.SYS':101, '.PRMT':102, '.LDC.64':103,
'.I2F.RP':104, '.BREAK':105, '.ISETP.GT.U32.OR':106, '.FSETP.GTU.FTZ.AND': 107, 
'.FSETP.NEU.FTZ.AND':108,'.P2R':109,'.ISETP.LE.AND':110,'.WARPSYNC':111
  }
