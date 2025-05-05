-- 
local file_proto = Proto("file_protocol", "File Transfer Protocol")
local gbn_proto = Proto("gbn", "Go-Back-N Protocol")

local f_op         = ProtoField.uint8("file.op", "Operation", base.DEC, {[0] = "Upload", [1] = "Download"})
local f_name_size  = ProtoField.uint8("file.name_size", "File Name Size", base.DEC)
local f_name       = ProtoField.string("file.name", "File Name")
local f_protocol   = ProtoField.uint8("file.protocol", "Error Recovery Protocol", base.DEC, {[0] = "Stop-and-Wait", [1] = "Go-Back-N"})
local f_file_size  = ProtoField.uint24("file.size", "File Size", base.DEC)
local f_error      = ProtoField.uint8("file.error", "Error Code", base.DEC, {[0] = "OK", [1] = "ERROR"})
local f_port       = ProtoField.uint16("file.port", "Port", base.DEC)

local gbn_seq = ProtoField.uint16("gbn.seq", "Sequence Number", base.DEC)
local gbn_ack = ProtoField.uint16("gbn.ack", "ACK Number", base.DEC)
local gbn_data = ProtoField.bytes("gbn.data", "Data")

file_proto.fields = {f_op, f_name_size, f_name, f_protocol, f_file_size, f_error, f_port}
gbn_proto.fields = {gbn_seq, gbn_ack, gbn_data}

local function combined_dissector(buffer, pinfo, tree)
    local length = buffer:len()
    if length < 4 then return false end

    local first = buffer(0,1):uint()

    -- file_protocol Response
    if length == 6 and (first == 0 or first == 1) then
        local subtree = tree:add(file_proto, buffer(), "File Transfer Response")
        subtree:add(f_error, buffer(0,1))
        subtree:add(f_port, buffer(1,2))
        subtree:add(f_file_size, buffer(3,3))
        pinfo.cols.protocol = "RESPONSE"
        return true

    -- file_protocol Request
    elseif (first == 0 or first == 1) then
        local name_len = buffer(1,1):uint()
        local expected_len = 2 + name_len + 1 + 3

        if length == expected_len then
            local subtree = tree:add(file_proto, buffer(), "File Transfer Request")
            subtree:add(f_op, buffer(0,1))
            subtree:add(f_name_size, buffer(1,1))
            subtree:add(f_name, buffer(2, name_len))
            subtree:add(f_protocol, buffer(2 + name_len, 1))
            subtree:add(f_file_size, buffer(2 + name_len + 1, 3))
            pinfo.cols.protocol = "REQUEST"
            return true
        end
    end

    -- Posible GBN
    if length >= 4 then
        local seq = buffer(0,2):uint()
        local ack = buffer(2,2):uint()

        local subtree = tree:add(gbn_proto, buffer(), "GBN Packet")
        subtree:add(gbn_seq, buffer(0,2))
        subtree:add(gbn_ack, buffer(2,2))
        if length > 4 then
            subtree:add(gbn_data, buffer(4))
        end
        pinfo.cols.protocol = "RDT"
        return true
    end

    return false
end

-- Registro heurístico
file_proto:register_heuristic("udp", combined_dissector)