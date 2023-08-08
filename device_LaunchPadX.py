# name=Novation Launchpad X v2
# Version 1.0
import patterns
import mixer
import device
import transport
import arrangement
import general
import launchMapPages
import playlist
import ui
import midi
import utils
import math
import time
import lpx_tools

MaxInt = 2147483647
grid_width = 10
grid_height = 10
grid_area = grid_height * grid_width
# clips
ClipsX = 1
ClipsY = 1
ClipsW = 9
ClipsH = 9
SceneY = 8
# solid clips
SClipsX = 1
SClipsY = 1
SClipsW = 8
SClipsH = 8
# overview
OverX = 1
OverY = 1
OverW = 8
OverH = 8
# overlay
LayX = ClipsX
LayY = ClipsY
LayW = ClipsW
LayH = ClipsH
# stride
PadsStride = 10
ForbiddenPads = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90]

MaxPads = grid_width * grid_height
NumBtns = 12

Btn_Up = 0x5B
Btn_Down = 0x5C
Btn_Left = 0x5D
Btn_Right = 0x5E

# BEGIN--------
Btn_Session = 0x5F
Btn_Note = 0x60
Btn_Custom = 0x61
Btn_CapMidi = 0x62

Btn_Logo = 0x63
Btn_Volume = 0x59
Btn_Pan = 0x4F
Btn_SendA = 0x45
Btn_SendB = 0x3B
Btn_StopClip = 0x31
Btn_Mute = 0x27
Btn_Solo = 0x1D
Btn_RecordArm = 0x13
# END--------

Btn_Snap = 0
Btn_ScenePlus = 1
Btn_Scene = 2
Btn_Queue = 3
Btn_Overview = 4
Btn_Spare = 5
Btn_Play = 6
Btn_Stop = 7
Btn_TapTempo = 8
Btn_TempoNudgePlus = 9
Btn_TempoNudgeMin = 10
Btn_VelLock = 11
Btn_Drums = 12
Btn_Keys = 13
Btn_User = 14

LPBlinkShift = 24
LPBlink1 = 1 << LPBlinkShift
LPBlink2 = 2 << LPBlinkShift
LPBlink3 = 3 << LPBlinkShift
LPBlink4 = 4 << LPBlinkShift
LPBlinkMask = 0xFF << LPBlinkShift
faderChangedFromDAW = False
initialTrack = mixer.trackNumber()
initialTrackTEMP = initialTrack
mixer_touched = False

lpx = lpx_tools.LPX()


class TBtnInfo():
	def __init__(self, Id, Num, Flags, Col):
		#print('\nTBtnInfo func')
		self.Id = Id
		self.Num = Num
		self.Flags = Flags
		self.Col = Col  # off, on, held

	def GetYX(self):
		#print('GetYX func')
		return utils.DivModU(self.Num, grid_width)

BtnInfo = [TBtnInfo(Btn_Snap, 3, 0 ,(0x040404, 0x3F3F3F, 0x000000)), TBtnInfo(Btn_ScenePlus, 8 ,1 ,(0x020000, 0x1C0000 | LPBlink4, 0x3F0A00)), TBtnInfo(Btn_Scene, 7, 1, (0x020000, 0x1C0000 | LPBlink4, 0x3F0A00)), TBtnInfo(Btn_Queue, 6, 1, (0x000100, 0x000A00 | LPBlink4, 0x002C10)), TBtnInfo(Btn_Overview, 5, 1 ,(0x000004, 0x000020 | LPBlink4, 0x00023F)), TBtnInfo(Btn_Spare, 6, 0, (0x040404, 0x3F3F3F, 0x000000)), TBtnInfo(Btn_Play, 70, 0, (0, 0, 0)), TBtnInfo(Btn_Stop, 80, 0, (0x000200, 0x001C00, 0x000000)), TBtnInfo(Btn_TapTempo, 30, 0, (0x000102, 0x00163F, 0x000000)), TBtnInfo(Btn_TempoNudgePlus, 40, 0, (0x000102, 0x00163F | LPBlink4, 0x000000)), TBtnInfo(Btn_TempoNudgeMin, 50, 0, (0x000102, 0x00163F | LPBlink4, 0x000000)), TBtnInfo(Btn_VelLock, 60, 1, (0x020001, 0x1C0010 | LPBlink4, 0x3F0A20))]#, TBtnInfo(Btn_Drums, 96, 1, (0x020001, 0x1C0010 | LPBlink4, 0x3F0A20)), TBtnInfo(Btn_Keys, 97, 1, (0x020001, 0x1C0010 | LPBlink4, 0x3F0A20)), TBtnInfo(Btn_User, 98, 1, (0x020001, 0x1C0010 | LPBlink4, 0x3F0A20))]
LeftBtnInfo = [TBtnInfo(Btn_Snap, 3, 0 ,(0x040404, 0x3F3F3F, 0x000000)), TBtnInfo(Btn_ScenePlus, 8 ,1 ,(0x020000, 0x1C0000 | LPBlink4, 0x3F0A00)), TBtnInfo(Btn_Scene, 7, 1, (0x020000, 0x1C0000 | LPBlink4, 0x3F0A00)), TBtnInfo(Btn_Queue, 6, 1, (0x000100, 0x000A00 | LPBlink4, 0x002C10)), TBtnInfo(Btn_Overview, 5, 1 ,(0x000004, 0x000020 | LPBlink4, 0x00023F)), TBtnInfo(Btn_Spare, 6, 0, (0x040404, 0x3F3F3F, 0x000000)), TBtnInfo(Btn_Play, 70, 0, (0, 0, 0)), TBtnInfo(Btn_Stop, 80, 0, (0x000200, 0x001C00, 0x000000)), TBtnInfo(Btn_TapTempo, 30, 0, (0x000102, 0x00163F, 0x000000)), TBtnInfo(Btn_TempoNudgePlus, 40, 0, (0x000102, 0x00163F | LPBlink4, 0x000000)), TBtnInfo(Btn_TempoNudgeMin, 50, 0, (0x000102, 0x00163F | LPBlink4, 0x000000)), TBtnInfo(Btn_VelLock, 60, 1, (0x020001, 0x1C0010 | LPBlink4, 0x3F0A20))]#, TBtnInfo(Btn_Drums, 96, 1, (0x020001, 0x1C0010 | LPBlink4, 0x3F0A20)), TBtnInfo(Btn_Keys, 97, 1, (0x020001, 0x1C0010 | LPBlink4, 0x3F0A20)), TBtnInfo(Btn_User, 98, 1, (0x020001, 0x1C0010 | LPBlink4, 0x3F0A20))]
RightBtnInfo = [TBtnInfo(Btn_Snap, 3, 0 ,(0x040404, 0x3F3F3F, 0x000000)), TBtnInfo(Btn_ScenePlus, 8 ,1 ,(0x020000, 0x1C0000 | LPBlink4, 0x3F0A00)), TBtnInfo(Btn_Scene, 7, 1, (0x020000, 0x1C0000 | LPBlink4, 0x3F0A00)), TBtnInfo(Btn_Queue, 6, 1, (0x000100, 0x000A00 | LPBlink4, 0x002C10)), TBtnInfo(Btn_Overview, 5, 1 ,(0x000004, 0x000020 | LPBlink4, 0x00023F)), TBtnInfo(Btn_Spare, 6, 0, (0x040404, 0x3F3F3F, 0x000000)), TBtnInfo(Btn_Play, 79, 0, (0, 0, 0)), TBtnInfo(Btn_Stop, 89, 0, (0x000200, 0x001C00, 0x000000)), TBtnInfo(Btn_TapTempo, 39, 0, (0x000102, 0x00163F, 0x000000)), TBtnInfo(Btn_TempoNudgePlus, 49, 0, (0x000102, 0x00163F | LPBlink4, 0x000000)), TBtnInfo(Btn_TempoNudgeMin, 59, 0, (0x000102, 0x00163F | LPBlink4, 0x000000)), TBtnInfo(Btn_VelLock, 69, 1, (0x020001, 0x1C0010 | LPBlink4, 0x3F0A20))]#, TBtnInfo(Btn_Drums, 96, 1, (0x020001, 0x1C0010 | LPBlink4, 0x3F0A20)), TBtnInfo(Btn_Keys, 97, 1, (0x020001, 0x1C0010 | LPBlink4, 0x3F0A20)), TBtnInfo(Btn_User, 98, 1, (0x020001, 0x1C0010 | LPBlink4, 0x3F0A20))]

BlinkColT = ((0x280102, 0x3F3F3F), (0x100002, 0x18002F), (0x100100, 0x181000), (0x000000, 0x3F3F3F))



class TLaunchPadX():
	def __init__(self):
		self.Shift = False
		self.ClipOfs = 0
		self.TrackOfs = 0
		self.TrackOfs_Spare = 0
		self.ClipOfs_Spare = 0
		self.BlockOfs = False # make arrows work in pages
		self.PrevClipOfs = 0
		self.ClipOfsPerfomance = 0
		self.TrackOfsPerfomance = 0
		self.BtnT = bytearray(NumBtns)
		self.ArrowT = bytearray(4)
		self.BlinkOnBars = 0
		self.BtnLastClip = [[0 for x in range(grid_width)] for y in range(grid_height)]
		self.BtnLastPressure = [[0 for x in range(grid_width)] for y in range(grid_height)]

		self.BtnMap = [[0 for x in range(grid_width)] for y in range(grid_height)]
		self.AnimBtnMap = [[0 for x in range(grid_width)] for y in range(grid_height)]
		self.ScreenCapBtnMap= [[0 for x in range(grid_width)] for y in range(grid_height)]
		self.OldBtnMap = [[0 for x in range(grid_width)] for y in range(grid_height)]

		self.NoFullRefresh = False
		self.BeatPos = 0
		self.BlinkLight = 2
		self.CurLayout = 0
		self.CurSession = ''

		self.BtnMapMode = 0 #animation
		self.BtnMapModeRefCount = 0

		self.ScreenCapZoom = 32
		#todo ScreenCapDIB1, ScreenCapDIB2: TDIB
		#todo ScreenDC: HDC
		self.ScreenCapTime = 0
		self.ColScaleT = bytearray(256) 
		
		self.LeftBtnColumnToggle = False


		self.is_mixerMode_enabled = False
		self.is_performance_mode = playlist.getPerformanceModeState()
		self.is_sessionMode_active = False
		self.start_time = 0
		


	def ResetBtnLastClip(self):
		#print('\nResetBtnLastClip func')
		for y in range(0, grid_width):
			for x in range(0, grid_height):
				self.BtnLastClip[x][y] = utils.TClipLauncherLastClip(MaxInt, MaxInt, MaxInt)



	def ResetBtnMap(self, BtnMapObj, val):
		#print('\nResetBtnMap func')
		for y in range(0, grid_height):
			for x in range(0, grid_width):
				BtnMapObj[y][x] = val



	def UpdateBlinking(self):  #check if any blinking button
		# #print('\nUpdateBlinking func')
		for y in range(0, grid_height):
			for x in range(0, grid_width):
				if self.BtnMap[y][x] > 1:
					self.FullRefresh_Btn()
					return


	def Reset(self):
		print('\nReset func')
		self.ResetBtnMap(self.BtnMap, 0)
		self.ResetBtnMap(self.AnimBtnMap, 0)
		self.ResetBtnMap(self.ScreenCapBtnMap, 0)
		self.ResetBtnMap(self.OldBtnMap, 0xFF)
		self.ResetBtnLastClip()



	def FullRefresh_Btn(self):
		# #print('\n\nFullRefresh_Btn func')
		if (self.BtnMapMode < 2) & (self.BtnMapModeRefCount == 0):
			device.fullRefresh()



	def FullRefresh_Anim(self):
		#print('\n\nFullRefresh_Anim func')
		if ((self.BtnMapMode > 0) & (self.BtnMapMode < 3)) | (self.BtnMapModeRefCount != 0):
			device.fullRefresh()



	def SetOfs(self, SetTrackOfs, SetClipOfs):
		print('\n\nSetOfs func:',SetTrackOfs)
		Col1 = 0x010900
		Col2 = 0x090100


		self.TrackOfs = utils.Limited(SetTrackOfs, 0, playlist.trackCount() - grid_height)
		self.ClipOfs = utils.Limited(SetClipOfs, -launchMapPages.length() - 1, 0x10000)
		print(SetTrackOfs, playlist.trackCount() - grid_height,'-----------------TrackOfs:', self.TrackOfs, '  -----------ClipOfs:',self.ClipOfs)
		if device.isAssigned():
		# 	# page buttons
		# 	o = self.TrackOfs + 4
		# 	v = utils.Limited(o, 0, 256)
		# 	self.BtnMap[1][0] = utils.FadeColor(Col2, Col1, v)
		# 	self.BtnMap[2][0] = utils.FadeColor(Col1, Col2, v)

		# 	o = abs(self.ClipOfs) * 4
		# 	if self.ClipOfs < 0:
		# 		o = o * 4
		# 	v = utils.Limited(o, 0, 256)
		# 	self.BtnMap[0][1] = utils.FadeColor(Col2, Col1, v)
		# 	self.BtnMap[0][2] = utils.FadeColor(Col1, Col2, v)

			if self.ClipOfs < -1:
				launchMapPages.updateMap(-self.ClipOfs - 2)
			else:
				launchMapPages.checkMapForHiddenItem()
			self.OnUpdateLiveMode(playlist.trackCount())			

		if playlist.getDisplayZone() != 0:
			self.OnDisplayZone()


	def CheckSpecialSwitches(self):
		#print('CheckSpecialSwitches func')
		if (self.ArrowT[0] + self.ArrowT[1] + self.ArrowT[2] + self.ArrowT[3]) >= 0x7F * 4:
			self.BlockOfs = not self.BlockOfs
			self.SetOfs(0, 0)
			device.stopRepeatMidiEvent()



	def SetBtn(self, Index, Value):
		#print('\n\nSetBtn func')
		self.BtnT[Index] = Value

		v = BtnInfo[Index].Col[utils.Limited(Value, 0, 2)]
		if v != -1:
			y, x = BtnInfo[Index].GetYX()
			self.BtnMap[y][x] = v
			self.FullRefresh_Btn()

		if Index > Btn_Overview:
			if Index == Btn_Spare:
				if Value > 0:
					# utils.SwapInt(self.TrackOfs, self.TrackOfs_Spare)
					# utils.SwapInt(self.ClipOfs, self.ClipOfs_Spare)
					self.SetOfs(self.TrackOfs, self.ClipOfs)

				self.SetBtn(Btn_Overview, Value)
		else:
			#overview
			self.OnUpdateLiveMode(playlist.trackCount())
			device.stopRepeatMidiEvent() #  in case arrows were held
			playlist.lockDisplayZone(0, Value > 0)
		


	def SwitchLedsOff(self):
		#print('\n\nSwitchLedsOff func')
		t = (0x030C02292000F0).to_bytes(7 + 3 * MaxPads, byteorder='little')
		s = bytearray(t)
		m = 7
		for y in range(0, grid_height):
			y2 = y * 10
			for x in range(0, grid_width):
				p = 90 - y2 + x
				ForbiddenPads = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90]
				if (not (p in ForbiddenPads)):
					s[m] = 0
					s[m + 1] = y2 + x
					s[m + 2] = 0
					m += 3
		s[m] = 0xF7
		s = s[: m + 1]
		device.midiOutSysex(bytes(s))


	def FixColor(self, Color):
		# print('\n\nFixColor func')
		r, g, b = utils.ColorToRGB(Color)
		r = self.ColScaleT[r]
		g = self.ColScaleT[g]
		b = self.ColScaleT[b]
		#r = round((r / 256) * 127)
		#g = round((g / 256) * 127)
		#b = round((b / 256) * 127)
		return utils.RGBToColor(r, g, b)






	def OnMidiIn(self, event):
		print ('\nOnMidiIn func', event.status )

		data = event.data1

		if event.status == midi.MIDI_BEGINSYSEX:
			# print ('midi in sysex', len(event.sysex), event.sysex[0], event.sysex[1], event.sysex[2], event.sysex[3], event.sysex[4], event.sysex[5], event.sysex[6], event.sysex[7], event.sysex[8], event.sysex[9]) #, event.sysex[10], event.sysex[11], event.sysex[12], event.sysex[13], event.sysex[14], event.sysex[15], event.sysex[16])
			#layout change
			print(len(event.sysex),'...and..',event.sysex[5], event.sysex[7],'-------layout BEFORE change:',event.sysex)
			if (len(event.sysex) == 9) & (event.sysex[5] == 0x0C):
				print('-------layout AFTER change:',event.sysex[7])
				self.CurLayout = event.sysex[7]
			event.handled = True
		else:
			# print('onmidiin else')
			event.handled = False



	def OnMidiMsg(self, event):
		print('OnMidiMsg func ---- READ MIDI INPUT contro n:',event.controlNum)
		# print ("controlNum: {}, \n controlVal: {}, \n data1: {}, \n data2: {}, \n handled:{}, \n inEv: {}, \n isIncrement: {}, \n midiChan: {}, \n midiChanEx:{}, \
		#  \n midiId: {}, \n note: {}, \n outEv: {}, \n pitchBend:{}, \n pmeFlags: {}, \n port: {}, \n pressure:{}, \n progNum: {}, \n res: {}, \n senderId: {}, \
		# 	  \n status:{}, \n sysex: {}, \n timestamp: {}, \n velocity: {}, \n write:{}".format(
		# 	event.controlNum, event.controlVal, event.data1, event.data2, event.handled, event.inEv, event.isIncrement, event.midiChan, 
		# 	event.midiChanEx, event.midiId, event.note, event.outEv, event.pitchBend, event.pmeFlags, event.port, event.pressure, event.progNum, 
		# 	event.res, event.senderId, event.status, event.sysex, event.timestamp, event.velocity, event.write ))
		data = event.data1
		# print('presssed w event:',dir(event))
		# print('presssed w data1:', data, '  -->', hex(data))
		global faderChangedFromDAW, initialTrack
		# send data to DAW
		if 0 <= event.controlNum <= 7:
			if event.controlNum == 0:
				mixer.setTrackVolume((mixer.trackNumber()), (event.controlVal / 127) )
			elif event.controlNum == 1:
				mixer.setTrackVolume((mixer.trackNumber() + 1), (event.controlVal / 127) ) 
			elif event.controlNum == 2:
				mixer.setTrackVolume((mixer.trackNumber() + 2), (event.controlVal / 127) )
			elif event.controlNum == 3:
				mixer.setTrackVolume((mixer.trackNumber() + 3), (event.controlVal / 127) )
			elif event.controlNum == 4:
				mixer.setTrackVolume((mixer.trackNumber() + 4), (event.controlVal / 127) )
			elif event.controlNum == 5:
				mixer.setTrackVolume((mixer.trackNumber() + 5), (event.controlVal / 127) )
			elif event.controlNum == 6:
				mixer.setTrackVolume((mixer.trackNumber() + 6), (event.controlVal / 127) )
			elif event.controlNum == 7:
				mixer.setTrackVolume((mixer.trackNumber() + 7), (event.controlVal / 127) )
			faderChangedFromDAW = False
		elif 8 <= event.controlNum <= 15:
			print('_____control value:', event.controlVal, round(event.controlVal / 127, 2) )
			trackPan = round(event.controlVal / 127, 2)
			if trackPan < 0.5:
				trackPan = -(1-trackPan)
			elif event.controlVal == 0.5:
				trackPan = 0
				print('____________________now val is:', trackPan)
			if event.controlNum == 8:
				mixer.setTrackPan((mixer.trackNumber()), trackPan )
			elif event.controlNum == 9:
				mixer.setTrackPan((mixer.trackNumber() + 1), (event.controlVal / 127) ) 
			elif event.controlNum == 10:
				mixer.setTrackPan((mixer.trackNumber() + 2), (event.controlVal / 127) )
			elif event.controlNum == 11:
				mixer.setTrackPan((mixer.trackNumber() + 3), (event.controlVal / 127) )
			elif event.controlNum == 12:
				mixer.setTrackPan((mixer.trackNumber() + 4), (event.controlVal / 127) )
			elif event.controlNum == 13:
				mixer.setTrackPan((mixer.trackNumber() + 5), (event.controlVal / 127) )
			elif event.controlNum == 14:
				mixer.setTrackPan((mixer.trackNumber() + 6), (event.controlVal / 127) )
			elif event.controlNum == 15:
				mixer.setTrackPan((mixer.trackNumber() + 7), (event.controlVal / 127) )
			faderChangedFromDAW = False
		if event.data2 > 0:
			self.start_time = time.time()
		else:
			print('-----------initial BEFORE:', initialTrack)
			if data  == Btn_Up:
				print('OnMidiMsg presssed Btn_Up')
			elif data == Btn_Down:
				print('OnMidiMsg presssed Btn_Down')
			elif data == Btn_Left and initialTrack > 1:
				event.handled = True
				ui.previous()
				initialTrack = initialTrack - 1
				ui.miDisplayRect(mixer.trackNumber(),mixer.trackNumber()+7,1000)
				print('-----------initial AFTER L:', initialTrack)
				print('OnMidiMsg presssed Btn_Left')
			elif data == Btn_Right and initialTrack+7 < 125:
				event.handled = True
				ui.next()
				initialTrack = initialTrack + 1
				ui.miDisplayRect(mixer.trackNumber(),mixer.trackNumber()+7,1000)
				print('-----------initial AFTER R:', initialTrack)
				print('OnMidiMsg presssed Btn_Right')
			elif data == Btn_Session:
				if self.is_sessionMode_active is True:
					lpx.toggle_session(self.is_performance_mode)
					print('+++toggled')
				else:
					lpx.recall_last_session(self.is_performance_mode)
					print('back to last session')
					self.is_sessionMode_active = True



				# print('IS MIXER ENABLED:',self.is_mixerMode_enabled)
				# if self.is_mixerMode_enabled is True:
				# 	print('move to session')
				# 	# channge session color to green and then enabled it
				# 	device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x14, 0x59, 0x01, 0xF7]))
				# 	device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x00, 0xF7]))
				# 	self.is_mixerMode_enabled = False
				# 	self.CurSession = lpx_tools.Layout.SESSION_LAYOUT.value.PAGES
				# else:
				# 	print('move to mixer')
				# 	# channge session color to orange and then enabled it
				# 	device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x14, 0x0C, 0x01, 0xF7]))
				# 	device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x0D, 0xF7]))
				# 	self.is_mixerMode_enabled = True
				# 	self.CurSession = lpx_tools.Layout.SESSION_LAYOUT.value.MIXER
				event.handled = True
				print('OnMidiMsg presssed Btn_Session')
			elif data == Btn_Note:
				print('OnMidiMsg presssed Btn_Note')
				self.is_sessionMode_active = False
				self.CurSession = lpx_tools.Layout.NOTE
				print('SESSION::::', self.CurSession)
			elif data == Btn_Custom:
				print('OnMidiMsg presssed Btn_Custom')
			elif data == Btn_CapMidi:
				# o = int(event.data2 > 0) * 2
				
				# event.handled = True
				interval = time.time() - self.start_time
				is_playing = transport.isPlaying()
				is_recording = transport.isRecording()
				is_double_click = device.isDoubleClick(data)
				capture_midi_pad = lpx.get_pad(lpx_tools.Pad_ID.CAPTURE_MIDI)
				print('caputred pad: ', capture_midi_pad.name)

				if interval < 0.5:
					if is_double_click:
						transport.stop()
						# device.midiOutSysex(bytes([0xB0, 98, 0x4F]))
						capture_midi_pad.trigger_state('idle')
						print('stop')
						print('============Btn_CapMidi is doubleckick:',is_double_click)
						event.handled = True
					else:
						if is_playing:
							print('pause:',is_playing)
							# device.midiOutSysex(bytes([0xB0, 98, 0x0D]))
							capture_midi_pad.trigger_state('double_click')
						else:
							print('play:',is_playing)
							# device.midiOutSysex(bytes([0xB0, 98, 0x57]))
							capture_midi_pad.trigger_state('active')
						transport.globalTransport(midi.FPT_Play, midi.PME_System, event.pmeFlags)
						print('------------------>>>>> LESS THAN 1:',interval)
						event.handled = True
				else:
					if is_recording:
							print('stop record:',is_recording)
							# device.midiOutSysex(bytes([0xB0, 98, 0x57]))
							capture_midi_pad.trigger_state('idle')
					else:
						print('record:',is_recording)
						# device.midiOutSysex(bytes([0xB0, 98, 0x48]))
						capture_midi_pad.trigger_state('long_click')
					transport.globalTransport(midi.FPT_Record, midi.PME_System, event.pmeFlags)
					print('------------------>>>>> BIGGER THAN 1:',interval)
					event.handled = True
				
				print('OnMidiMsg presssed Btn_CapMidi')
			elif data == Btn_Logo:
				print('OnMidiMsg presssed Btn_Logo')
			elif data == Btn_Volume:
				print('============Btn_Volume is doubleckick:',device.isDoubleClick(data))
				device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x01, 0x00, 0x00, 
				0x00, 0x00, 0, 0x05,
				0x01, 0x00, 1, 0x13, 
				0x02, 0x00, 2, 0x21, 
				0x03, 0x00, 3, 0x29,
				0x04, 0x00, 4, 0x37, 
				0x05, 0x00, 5, 0x45, 
				0x06, 0x00, 6, 0x53, 
				0x07, 0x00, 7, 0x61, 0xF7]))
				
				lpx.get_pad(lpx_tools.Pad_ID.PAN).trigger_state('idle')
				lpx.get_pad(lpx_tools.Pad_ID.VOLUME).trigger_state('active')
				event.handled = True
				print('OnMidiMsg presssed Btn_Volume')
			elif data == Btn_Pan:
				device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x01, 0x00, 0x01, 
				0x00, 0x01, 8, 0x05,
				0x01, 0x01, 9, 0x13, 
				0x02, 0x01, 10, 0x21, 
				0x03, 0x01, 11, 0x29,
				0x04, 0x01, 12, 0x37, 
				0x05, 0x01, 13, 0x45, 
				0x06, 0x01, 14, 0x53, 
				0x07, 0x01, 15, 0x61, 0xF7]))
				lpx.get_pad(lpx_tools.Pad_ID.PAN).trigger_state('active')
				lpx.get_pad(lpx_tools.Pad_ID.VOLUME).trigger_state('idle')
				event.handled = True
				print('OnMidiMsg presssed Btn_Pan')
			elif data == Btn_SendA:
				print('OnMidiMsg presssed Btn_Btn_SendA')
			elif data == Btn_SendB:
				print('OnMidiMsg presssed Btn_SendB')
			ColT = (0x000000, 0x2F0018 | LPBlink2)

			if event.midiChan > 0:
				#print('OnMidiMsg - midiChan > 0')
				return


		


		### SYSTEM
		if (event.data1 == Btn_Up) | (event.data1 == Btn_Down): #------> track offset
			#print('\nOnMidiMsg - track offset UP or DOWN')
			if (event.data1 == Btn_Up):
				#print('OnMidiMsg - track Btn_Up')
				a = 0
			else:	
				#print('OnMidiMsg - track Btn_Down')
				a = 1
			event.handled = True
			BlockPages = (self.BtnT[Btn_Overview] > 0) | self.BlockOfs
			m = 150 + int(BlockPages) * 350 # faster in 1-pad increments
			device.repeatMidiEvent(event, m, m)

			if (event.data2 > 0) & (event.pmeFlags & midi.PME_System != 0):
				#print('OnMidiMsg - track event.data2 > 0) & (event.pmeFlags & midi.PME_System')
				m = a * 2 - 1
				
				if BlockPages:
					print('++++++ - track BlockPages')
					m = m * OverH
				print('call it UD')
				self.SetOfs(self.TrackOfs + m, self.ClipOfs)
				# self.BtnT[Btn_Overview] = int(self.BtnT[Btn_Overview] > 0) * 2 # so that session btn works as held
				
				# if self.ClipOfs >= 0:
				# 	#print('OnMidiMsg - track self.ClipOfs >= 0')
				# 	self.ClipOfsPerfomance = self.ClipOfs
				# self.TrackOfsPerfomance = self.TrackOfs
			# self.ArrowT[a] = event.data2

			print('self.ClipOfsPerfomance:', self.ClipOfsPerfomance,'__self.PrevClipOfs:', self.PrevClipOfs,' __self.ClipOfs:',self.ClipOfs)
			# self.CheckSpecialSwitches()
			# playlist.lockDisplayZone(1 + a, event.data2 >= 0)
			
			return



		elif (event.data1 == Btn_Left) | (event.data1 == Btn_Right): #------> performance clip offset
			#print('\nOnMidiMsg - clipoofset L or R')
			if event.data1 == Btn_Left and self.ClipOfsPerfomance <= 0:
				return

			a = event.data1 - Btn_Left
			event.handled = True
			BlockPages = (self.BtnT[Btn_Overview] > 0) | self.BlockOfs
			m = 150 + int(BlockPages) * 350 # faster in 1-pad increments
			device.repeatMidiEvent(event, m, m)
			if (event.data2 > 0) & (event.pmeFlags & midi.PME_System != 0):
				#print('OnMidiMsg - clip data2 > 0')
				m = (a) * 2 - 1
				if self.ClipOfs >= 0:
					print('OnMidiMsg - clip clipOfs >= 0')
					if (self.ClipOfs == 0) & (m == -1):
						#print('OnMidiMsg - clip self.ClipOfs == 0) & (m == -1 SWITCHED TO NEW PAGE')
						o = -1
					else:
						#print('OnMidiMsg - clip elsezz')
						if BlockPages:
							#print('OnMidiMsg - clip BlockPages')
							m = m * OverW
						o = max(self.ClipOfs + m, 0)
				else:
					print('OnMidiMsg - clip self.ClipOfs < 0:',self.ClipOfs)
					o = self.ClipOfs + m
				print('call it LR')
				self.SetOfs(self.TrackOfs, o)
				self.BtnT[Btn_Overview] = int(self.BtnT[Btn_Overview] > 0) * 2 # so that session btn works as held
				self.TrackOfsPerfomance = self.TrackOfs
				if self.ClipOfs >= 0:
					print('OnMidiMsg - clip still ClipOfs >= 0')
					self.ClipOfsPerfomance = self.ClipOfs
				self.PrevClipOfs = self.ClipOfs
				if self.ClipOfs <= 0:
					print('OnMidiMsg - clip well ClipOfs <= 0')
					# self.ClipOfsPerfomance = 0
					device.stopRepeatMidiEvent()
				print('m:',m,'_self.ClipOfsPerfomance:', self.ClipOfsPerfomance,'__self.PrevClipOfs:', self.PrevClipOfs,' __self.ClipOfs:',self.ClipOfs)
			self.ArrowT[2 + a] = event.data2
			
			self.ArrowT[3] = event.data2
			self.CheckSpecialSwitches()
			print('a:',1+a, '__evt.data:',event.data2)
			playlist.lockDisplayZone(1 + a, event.data2 >= 0)
			return

		elif event.midiId in [midi.MIDI_NOTEON, midi.MIDI_NOTEOFF, midi.MIDI_CONTROLCHANGE]:

			if event.midiId == midi.MIDI_NOTEOFF:
				event.data2 = 0
			elif (self.BtnT[Btn_VelLock] > 0) & (event.data2 > 0):
				event.data2 = 0x7F

			y = event.data1 // PadsStride
			x = event.data1 + 90 - y * PadsStride * 2 # top-down index
			# system buttons
			for n in range(1, len(BtnInfo)):
				if BtnInfo[n].Num == x:
					event.handled = True
					m2 = self.BtnT[n]
					
			
			# live mode
			x = event.data1 - y * PadsStride - ClipsX
			y = ClipsH - ClipsY - y
			if (x >= grid_width) | (y >= grid_height):
				return


			if self.ClipOfs < -1:
				# custom pages
				x2 = y * LayW + x
				m = -self.ClipOfs - 2
				if x2 <= launchMapPages.getMapCount(m):
					o = launchMapPages.getMapItemChannel(m, x2)
					if o > -128:
						m2 = event.data2
						if (m2 == 0) & (self.BtnT[Btn_ScenePlus] > 0):
							m2 = -MaxInt # user1=hold
						launchMapPages.processMapItem(event, m, x2, m2)
			
			else: # PERFORMANCE TRIGGER

				if (event.pmeFlags & midi.PME_System_Safe != 0):
					x2 = x
					y2 = y + self.TrackOfs + 1
					if self.ClipOfs >= 0:
						if event.data2 > 0:
							# clip launch
							m = midi.TLC_MuteOthers | midi.TLC_Fill
							if y >= SceneY:
								y2 = 0
								m = m | midi.TLC_ColumnMode # column mode

							if x2 >= SClipsW:
								x2 = -1
							else:
								x2 += self.ClipOfs
							m = midi.TLC_MuteOthers | midi.TLC_Fill
							if self.BtnT[Btn_Queue] > 0:
								m = m | midi.TLC_Queue
							if self.BtnT[Btn_Snap] > 0:
								m = m | midi.TLC_GlobalSnap # snap
							if self.BtnT[Btn_ScenePlus] | (self.BtnT[Btn_Scene] > 0):
								m = m | midi.TLC_ColumnMode # column mode
								if self.BtnT[Btn_ScenePlus] == 0:
									m = m | midi.TLC_WeakColumnMode # weak
								elif self.BtnT[Btn_Scene] > 0:
									m = m | midi.TLC_TriggerCheckColumnMode # trigger-check

							if (self.BtnT[Btn_VelLock] > 0):
								playlist.triggerLiveClip(y2, x2, m)
							else:
								playlist.triggerLiveClip(y2, x2, m, event.data2 * (1 / 127))

							self.BtnLastClip[y][x].TrackNum = y2
							self.BtnLastClip[y][x].SubNum = x2
							self.BtnLastClip[y][x].Flags = m
					
						event.handled = True
			self.PrevClipOfs = self.ClipOfs
		else:
			event.handled = False
		


		
		# self.PrevClipOfs = self.ClipOfs
		



	def OnMidiOutMsg(self, event):
		print('\n\nOnMidiOutMsg func')
		data = event.data1
		if data  == Btn_Up:
			print('OnMidiOutMsg presssed Btn_Up')
		elif data == Btn_Down:
			print('OnMidiOutMsg presssed Btn_Down')
		elif data == Btn_Left:
			print('OnMidiOutMsg presssed Btn_Left')
		elif data == Btn_Right:
			print('OnMidiOutMsg presssed Btn_Right')
		elif data == Btn_Session:
			print('OnMidiOutMsg presssed Btn_Session')
		elif data == Btn_Note:
			print('OnMidiOutMsg presssed Btn_Note')
		elif data == Btn_Custom:
			print('OnMidiOutMsg presssed Btn_Custom')
		elif data == Btn_CapMidi:
			print('OnMidiOutMsg presssed Btn_CapMidi')
		elif data == Btn_Logo:
			print('OnMidiOutMsg presssed Btn_Logo')
		elif data == Btn_Volume:
			print('OnMidiOutMsg presssed Btn_Volume')
		elif data == Btn_Pan:
			print('OnMidiOutMsg presssed Btn_Pan')
		elif data == Btn_SendA:
			print('OnMidiOutMsg presssed Btn_Btn_SendA')
		elif data == Btn_SendB:
			print('OnMidiOutMsg presssed Btn_SendB')



	def OnDoFullRefresh(self):
		# print('\n\nOnDoFullRefresh func')
		TempBtnMap = [[0 for x in range(grid_width)] for y in range(grid_height + 1)]
		TempAnimBtnMap = [[0 for x in range(grid_width)] for y in range(grid_height + 1)]
		# print('--------LAYOUT:',self.CurLayout)
		if (self.CurLayout == 0) & device.isAssigned():
			TempBtnMapMode = self.BtnMapMode

			if TempBtnMapMode >= 3:
				for y in range(0, grid_height):
					for x in range(0, grid_width):
						TempBtnMap[y][x] = self.BtnMap[y][x]
				TempBtnMap[0][grid_width - 1] = self.BtnMap[0][grid_width - 1] # bottom light
			else:
				if TempBtnMapMode < 2:
					if self.BtnMapModeRefCount == 0:
						for y in range(0, grid_height):
							for x in range(0, grid_width):
								TempBtnMap[y][x] = self.BtnMap[y][x]
					else:
						TempBtnMapMode = 2
						TempBtnMap[0][grid_width - 1] = self.BtnMap[0][grid_width - 1] # bottom light

				if TempBtnMapMode > 0:
					for y in range(0, grid_height):
						for x in range(0, grid_width):
							TempAnimBtnMap[y][x] = self.AnimBtnMap[y][x]

				# adapt anim map
				if TempBtnMapMode > 0:
					for y in range(0, grid_height):
						for x in range(0, grid_width):
							print(y, ':y ---- x:',x)
							if y < 10 and x < 10:
								print(y, ':y --PASS-- x:',x)
								r, g, b = utils.ColorToRGB(TempAnimBtnMap[y][x])
								c = utils.HSVtoRGB(g , r , b )
								c = self.FixColor(c)
								if (TempBtnMapMode >= 2) | (c > 0):
									TempBtnMap[y][ x] = c

			# update blinking
			for y in range(0, grid_height):
				for x in range(0, grid_width):
					o = TempBtnMap[y][x]
					if o & LPBlinkMask != 0:
						TempBtnMap[y][x] = utils.FadeColor(o, BlinkColT[min(o >> LPBlinkShift, 3)][0], self.BlinkLight)

			# build SysEx
			t = (0x030C02292000F0).to_bytes(8 + 5 * MaxPads, byteorder='little')
			s = bytearray(t)
			m = 7

			for y in range(0, grid_height):
				y2 = y * 10
				for x in range(0, grid_width):
					p = 90 - y2 + x
					# add to the list
					if (TempBtnMap[y][x] != self.OldBtnMap[y][x]) & (not (p in ForbiddenPads)):
						s[m] = 144
						s[m + 1] = 90 - y2 + x
						s[m + 2], s[m + 3], xx = utils.ColorToRGB(TempBtnMap[y][x])
						m += 5

			# send it
			if m > 8:
				s[m] = 0xF7
				s = s[: m + 1]
				# isSession = device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0xF7]))
				# if isSession:
				device.midiOutSysex(bytes(s))
				# else:
				# 	device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x01, 0X00, 0X01, 0X01, 0xF7]))

				'''
				sf = ''
				for y in range(7, len(s)):
					sf = sf + str(s[y]) + ', '
					if (y - 6) % 5 == 0:
						#print(sf)
						sf = ''
				#print('---------------------')
				'''

			# backup
			for y in range(0, grid_height):
				for x in range(0, grid_width):
					self.OldBtnMap[y][x] = TempBtnMap[y][x]
		


	def OnDisplayZone(self):
		print('\n\nOnDisplayZone func')
		if (self.ClipOfs >= 0) & (playlist.getDisplayZone() != 0):
			playlist.liveDisplayZone(self.ClipOfs, self.TrackOfs + 1, self.ClipOfs + grid_width - 1, self.TrackOfs + 1 + grid_height, 1000)
		else:
			playlist.liveDisplayZone(-1, -1, -1, -1)



	def OnIdle(self):
		# #print('\n\nOnIdle func')
		BlinkSpeed = 0x20

		if device.isAssigned():
			# beat cycle (smooth fade)
			if transport.isPlaying() != midi.PM_Playing:
				v2 = math.sin((time.time() % BlinkSpeed) * math.pi / BlinkSpeed)
			else:
				v2 = mixer.getSongTickPos(midi.ST_Beat)
				v2 = math.sin(v2 * (math.pi / 2))

			v3 = mixer.getSongTickPos(midi.ST_PGB)
			v3 = 1 - v3
			c = utils.FadeColor(0x003F30, 0x000138, round(v3 * v3 * 256))

			# activity meters
			if (self.ClipOfs == -1) & (self.BtnT[Btn_Overview] == 0):
				for y in range(0, SClipsH):
					m = self.TrackOfs + y + 1
					v3 = playlist.getTrackActivityLevelVis(m) * 2
					for x in range(SClipsX, SClipsX + 2):
						self.BtnMap[SClipsY + y][ x] = utils.FadeColor(0x3F303F, 0x000000, utils.Limited(round(v3 * 256), 0, 256))
						v3 = v3 - 1

			if not self.NoFullRefresh:
				if self.BtnMapMode == 3:
					#print('time to full refr')
					self.FullRefresh_Btn()

				self.BlinkLight = round(v2 * v2 * 256)
				if (self.BtnMap[0][3] != c) | (self.BtnMap[0][grid_width - 1] != c):
					y, x = BtnInfo[Btn_Play].GetYX()
					self.BtnMap[y][x] = c
					self.BtnMap[0][grid_width - 1] = c
					self.FullRefresh_Btn()
				else:
					self.UpdateBlinking()
													
				for x in range(0, 9):
					if (self.BtnMap[0][x] != c):
						self.BtnMap[0][x] = c
						self.FullRefresh_Btn()
					else:
						self.UpdateBlinking()



	def OnRefresh(self, flags):
		print('\n\nOnRefresh func:', flags)
		self.is_performance_mode = playlist.getPerformanceModeState()
		print('-----====----peformance mode is:', playlist.getPerformanceModeState() == True)
		if flags & midi.HW_Dirty_RemoteLinks != 0:
			if self.ClipOfs < -1:
				self.SetOfs(self.TrackOfs, self.ClipOfs)
			launchMapPages.updateMap(-1)



	def OnSysEx(self, event):
		print('onSysEx func', event.sysex, event.senderId)




	def OnInit(self):
		print('\n\nOnInit func')
		NameStr = 'Novation Launchpad X v2'

		lpx.initialise_pads()
		
		for n in range(0, len(self.ColScaleT)):
			v = n / 255
			self.ColScaleT[n] = min(round(v * v * v * 255 * 0.9), 63)

		# init mapping
		launchMapPages.createOverlayMap(1, 8, LayW, LayH)

		for y in range(0, LayH):
			for x in range(0, LayW):
					launchMapPages.setMapItemTarget(-1, y * LayW + x, y * PadsStride + x + 1)

		if device.isAssigned():
			device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x10, 0x01, 0xF7]))
			device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x10, 0xF7]))

			# device.midiOutSysex(bytes([0x90, 0x62, 0x05]))
			# device.midiOutSysex(bytes([0x90, 0x58, 0x4D]))

			# switch off all LEDs
			self.SwitchLedsOff()
			print('---INIT w b4 page:',self.CurLayout)
			self.CurLayout = 0
			print('---INIT w aft page:',self.CurLayout)

		# load mapping
		# launchMapPages.init(NameStr, LayW, LayH)

		self.Reset()
		device.createRefreshThread()
		for n in range(1, len(self.BtnT)):
			self.SetBtn(n, self.BtnT[n])
		self.OnUpdateLiveMode(playlist.trackCount())
		self.SetOfs(self.TrackOfs, self.ClipOfs)



	def OnDeInit(self):
		print('\n\nOnDeInit func')
		device.destroyRefreshThread()
		self.Reset()

		if device.isAssigned():
			if self.CurLayout == 0:
				self.SwitchLedsOff()
			# set b   ack to live mode
			device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x10, 0x00, 0xF7]))
			device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x10, 0xF7]))


	def OnUpdateLiveMode(self, LastTrackNum):
		print('\n\nOnUpdateLiveMode func:', LastTrackNum)
		FirstTrackNum = 1
		StatusColT = [0, 0, 0, 0]
		LoopBtnColT = (0x3F0000, 0x002400, 0x000110, 0x000228, 0x00033F, 0x180018, 0x3F003F)
		TrigColT = (0x001000, 0x280800, 0x200018, 0x202020)
		SnapColT = (0x000420, 0x180000, 0x3F0000, 0x300808, 0x201010, 0x101818, 0x002020)
		OverviewColT = ((0x000000, 0x200000, 0x4200000), (0x000110, 0x00063F, 0x400063F))
		OnLight = 0x48
		OffLight = -0x60 #-0x1A
		R = utils.TRect(0, 0, 0, 0)
		R2 = utils.TRect(0, 0, 0, 0)

		if device.isAssigned():
			if (self.ClipOfs >= -1) | (self.BtnT[Btn_Overview] > 0):
				# if self.BtnT[Btn_Overview] > 0:
				# 	# overview
				# 	R2.Left = self.ClipOfs
				# 	if R2.Left < 0:
				# 		R2.Left -= 128
				# 	R2.Right = R2.Left + SClipsW - 1
				# 	R2.Top = 1 + self.TrackOfs
				# 	R2.Bottom = R2.Top + SClipsH - 1
				# 	for y in range(0, OverH + 1):
				# 		for x in range(0, OverW + 1):
				# 			v = OverviewColT[0][0]
				# 			if (x < OverW) & (y < OverH):
				# 				R.Left = x * SClipsW
				# 				R.Right = R.Left + SClipsW - 1
				# 				R.Top = 1 + y * SClipsH
				# 				R.Bottom = R.Top + SClipsH - 1
				# 				o = patterns.getBlockSetStatus(R.Left, R.Top, R.Right, R.Bottom)
				# 				v = OverviewColT[utils.RectOverlapEqual(R, R2)][o]
				# 			elif (x == SClipsW) & (y < SClipsH):
				# 				v = OverviewColT[y == (-1 - self.ClipOfs)][int(y <= launchMapPages.length())]
				# 			elif (y == SClipsH) & (x < SClipsW):
				# 				v = OverviewColT[x + 8 == (-1 - self.ClipOfs)][int(x + 8 <= launchMapPages.length())]
				# 			self.BtnMap[OverY + y][OverX + x] = v
				# else:
					# scene buttons
					y = SClipsH + 1
					for x in range(0, ClipsW):
						v = launchMapPages.getMapItemColor(-1,(y - 1) * ClipsW + x)
						if v < 0:
							v = 0x010000
						else:
							v = self.FixColor(v)
							
						xx = SClipsX + x
						yy = SClipsY + y - 1
						print(xx,'<------>', yy)
						self.BtnMap[yy][xx] = v


					Ofs = self.TrackOfs
					for y in range(max(FirstTrackNum - Ofs, 1), min(LastTrackNum - Ofs, SClipsH) + 1):  #todo
						StatusColT[2] = TrigColT[playlist.getLiveTriggerMode(y + Ofs)]

						if self.ClipOfs >= 0:
							# clips
							for x in range(0, ClipsW):
								v = launchMapPages.getMapItemColor(-1, (y - 1) * ClipsW + x)
								if v < 0:
									if x < SClipsW:
										m = self.ClipOfs + x
										o = playlist.getLiveBlockStatus(y + Ofs, m, midi.LB_Status_Simple)
										if o == 0:
											v = 0
										else:
											v = playlist.getLiveBlockColor(y + Ofs, m)
											if o > 1:
												v = utils.LightenColor(v, OnLight)
											else:
												v = utils.LightenColor(v, OffLight)

											v = self.FixColor(v)
										if o == 2:
											v = v | LPBlink1
									else:
										o = playlist.getLiveStatus(y + Ofs, midi.LB_Status_Simple)
										if o == 0:
											v = 0
										else:
											v = playlist.getLiveBlockColor(y + Ofs, -1)
											if o == 2:
												v = utils.LightenColor(v, 0x20)
											elif o > 1:
												v = utils.LightenColor(v, OnLight)
											else:
												v = utils.LightenColor(v, OffLight)

											v = self.FixColor(v)
								else:
									v = self.FixColor(v)
								self.BtnMap[SClipsY + y - 1][SClipsX + x] = v
						else:
							# track properties
							v = 0
							for x in range(0, ClipsW):
								if (x == 2) | (x == 3):
									v = SnapColT[min(playlist.getLivePosSnap(y + Ofs), len(SnapColT))-1]
								elif (x == 4) | (x == 5):
									v = SnapColT[min(playlist.getLiveTrigSnap(y + Ofs), len(SnapColT))-1]
								elif (x == 6) | (x == 7):
									v = LoopBtnColT[playlist.getLiveLoopMode(y + Ofs)]
								elif x == 8:
									v = StatusColT[2]
								else:
									continue
								self.BtnMap[SClipsY + y - 1][SClipsX + x] = v
								

							self.NoFullRefresh = True
							self.OnIdle() # activity meters
							self.NoFullRefresh = False
			else:
				#custom pages
				for y in range(0, LayH):
					for x in range(0, LayW):
						self.BtnMap[LayY + y][LayX + x] = self.FixColor(launchMapPages.getMapItemColor(-self.ClipOfs - 2, y * LayW + x))

			self.FullRefresh_Btn()




LaunchPadX = TLaunchPadX()

def OnInit():
	LaunchPadX.OnInit()

def OnDeInit():
	LaunchPadX.OnDeInit()

def OnMidiIn(event):
	LaunchPadX.OnMidiIn(event)

def OnMidiMsg(event):
	print('++++++++++++++++++++++ MIDI MSG +++++++++++++++++++++++++', event.data1, event.controlVal)
	
	LaunchPadX.OnMidiMsg(event)

def OnMidiOutMsg(event):
	LaunchPadX.OnMidiOutMsg(event)

def OnDoFullRefresh():
	LaunchPadX.OnDoFullRefresh()

def OnDisplayZone():
	LaunchPadX.OnDisplayZone()

def OnIdle():
	LaunchPadX.OnIdle()

def OnRefresh(Flags):
	print('OnRefresh FLAGS--->',Flags)
	global initialTrack, initialTrackTEMP
	if Flags == 263:
		initialTrackTEMP = initialTrack
		initialTrack = mixer.trackNumber()
		print('++touched initialTrack b4:', initialTrack)
	elif Flags == 4:
		initialTrack = initialTrackTEMP
		print('++and moved initialTrack aft:',initialTrack)

	trkVolume = round(mixer.getTrackVolume(mixer.trackNumber()), 2)
	trkPan = round(mixer.getTrackPan(mixer.trackNumber()), 2)
	# mixer.setTrackVolume((mixer.trackNumber()), (trkVolume) ) 

	print('TRACK VOL:',trkVolume)
	print('TRACK PAN:',trkPan)

	global faderChangedFromDAW
	# receive data from DAW
	if faderChangedFromDAW == True:
		trackVol0 = round(mixer.getTrackVolume(initialTrack) * 127)
		print('0 track:', mixer.getTrackVolume(initialTrack), trackVol0 )
		device.midiOutMsg(180, 4, 0, trackVol0)

		trackVol1 = round(mixer.getTrackVolume(initialTrack + 1) * 127)
		print('1 track:', trackVol1 )
		device.midiOutMsg(180, 4, 1, trackVol1)

		trackVol2 = round(mixer.getTrackVolume(initialTrack + 2) * 127)
		device.midiOutMsg(180, 4, 2, trackVol2)

		trackVol3 = round(mixer.getTrackVolume(initialTrack + 3) * 127)
		device.midiOutMsg(180, 4, 3, trackVol3)

		trackVol4 = round(mixer.getTrackVolume(initialTrack + 4) * 127)
		device.midiOutMsg(180, 4, 4, trackVol4)

		trackVol5 = round(mixer.getTrackVolume(initialTrack + 5) * 127)
		device.midiOutMsg(180, 4, 5, trackVol5)

		trackVol6 = round(mixer.getTrackVolume(initialTrack + 6) * 127)
		device.midiOutMsg(180, 4, 6, trackVol6)

		trackVol7 = round(mixer.getTrackVolume(initialTrack + 7) * 127)
		device.midiOutMsg(180, 4, 7, trackVol7)
	# print('track:', index, ' has changed.')
	faderChangedFromDAW = True
	LaunchPadX.OnRefresh(Flags)

def OnUpdateLiveMode(LastTrackNum):
	LaunchPadX.OnUpdateLiveMode(LastTrackNum)

def OnSysEx(event):
	LaunchPadX.OnSysEx(event)

def OnDirtyMixerTrack(index):
	print('OnDirtyMixerTrack initialTrack:', initialTrack)
	