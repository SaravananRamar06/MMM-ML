C ======================================================================
C  Offline test driver for the generated user materials, without
C  Abaqus or ANSYS. Compile with gfortran and one of
C      umat/jc_pinn_umat.f        (default: calls the Abaqus UMAT)
C      umat/jc_pinn_usermat3d.F   with -DANSYS (calls usermat3d)
C  Reads a mode number from standard input:
C   1  flow stress: N, then N rows "T log10rate rho G e"
C      -> prints SIG, DSIG for each row (calls JCPSIG)
C   2  uniaxial stress: PROPS(1..7), NTENS, NSTEP, EMAX
C      -> strain-controlled eps11 to EMAX, lateral stresses held at 0
C   3  tangent: PROPS(1..7), NTENS, EQPS0, STRESS0(NTENS),
C      DSTRAN(NTENS) -> DDSDDE from the UMAT, then the
C      central-difference derivative of the stress update
C  Mode 2 also prints the plastic strain PL(1), PL(2) kept by the
C  ANSYS wrapper (zero for Abaqus, which does not return it).
C  Stubs replace the solver utilities STDB_ABQERR, XIT, erhandler.
C ======================================================================
      PROGRAM UDRV
      IMPLICIT NONE
      INTEGER MODE
      READ(*,*) MODE
      IF (MODE .EQ. 1) CALL MFLOW
      IF (MODE .EQ. 2) CALL MUNI
      IF (MODE .EQ. 3) CALL MTAN
      END
C
      SUBROUTINE MFLOW
      IMPLICIT NONE
      INTEGER N, I, IERR
      DOUBLE PRECISION T, RL, RHO, G, E, SIG, DSIG
      READ(*,*) N
      DO I = 1, N
         READ(*,*) T, RL, RHO, G, E
         CALL JCPSIG(T, RL, RHO, G, E, SIG, DSIG, IERR)
         WRITE(*,'(2ES26.17E3,I3)') SIG, DSIG, IERR
      END DO
      END
C
      SUBROUTINE CALLU(NTENS, PROPS, STRESS, STATEV, DSTRAN, DDSDDE,
     1                 PNEWDT, PL)
      IMPLICIT NONE
      INTEGER NTENS, NDI, NSHR, NSTATV, NPROPS, JSTEP(4)
      DOUBLE PRECISION PROPS(7), STRESS(6), STATEV(4), DSTRAN(6),
     1 DDSDDE(6,6), PNEWDT, DDS(NTENS,NTENS), PL(6)
      INTEGER I, J
      DOUBLE PRECISION SSE, SPD, SCD, RPL, DDSDDT(6), DRPLDE(6),
     1 DRPLDT, STRAN(6), TIME(2), DTIME, TEMP, DTEMP, PREDEF(1),
     2 DPRED(1), COORDS(3), DROT(3,3), CELENT, DFGRD0(3,3),
     3 DFGRD1(3,3)
      CHARACTER*80 CMNAME
      INTEGER KEYCUT
      DOUBLE PRECISION SEDEL, SEDPL, EPSEQ, VAR0, TSSTIF(2), EPSZZ,
     1 CUTF
      VAR0 = 0.D0
      SEDEL = 0.D0
      SEDPL = 0.D0
      EPSEQ = 0.D0
      EPSZZ = 0.D0
      CUTF = 1.D0
      NDI = 3
      NSHR = NTENS - 3
      NSTATV = 4
      NPROPS = 7
      SSE = 0.D0
      SPD = 0.D0
      SCD = 0.D0
      DO I = 1, 6
         STRAN(I) = 0.D0
      END DO
      TIME(1) = 0.D0
      TIME(2) = 0.D0
      DTIME = 1.D0
      TEMP = PROPS(1)
      DTEMP = 0.D0
      CMNAME = 'JCPINN'
#ifdef ANSYS
      KEYCUT = 0
      CALL usermat3d(1, 1, 1, 1, 1, 1, 1, KEYCUT,
     & NDI, NSHR, NTENS, NSTATV, NPROPS,
     & TIME(2), DTIME, TEMP, DTEMP,
     & STRESS, STATEV, DDS, SEDEL, SEDPL, EPSEQ,
     & STRAN, DSTRAN, PL, PROPS, COORDS,
     & VAR0, DFGRD0, DFGRD1,
     & TSSTIF, EPSZZ, CUTF,
     & VAR0, VAR0, VAR0, VAR0, VAR0, VAR0, VAR0)
      IF (KEYCUT .EQ. 1) PNEWDT = 0.25D0
      IF (KEYCUT.EQ.0 .AND. EPSEQ.NE.STATEV(1)) STOP 3
#else
      CALL UMAT(STRESS,STATEV,DDS,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,PREDEF,DPRED,CMNAME,
     3 NDI,NSHR,NTENS,NSTATV,PROPS,NPROPS,COORDS,DROT,PNEWDT,
     4 CELENT,DFGRD0,DFGRD1,1,1,0,0,JSTEP,1)
#endif
      DO J = 1, NTENS
         DO I = 1, NTENS
            DDSDDE(I,J) = DDS(I,J)
         END DO
      END DO
      END
C
      SUBROUTINE MUNI
      IMPLICIT NONE
      INTEGER NTENS, NSTEP, IS, IT, K
      DOUBLE PRECISION PROPS(7), EMAX, STRESS(6), STATEV(4), S(6),
     1 SV(4), DSTRAN(6), D(6,6), DL2, DL3, A, B, C, DD, DET, R2, R3,
     2 X2, X3, EPS11, PNEWDT, PL(6), PLT(6)
      READ(*,*) (PROPS(K), K=1,7)
      READ(*,*) NTENS, NSTEP, EMAX
      DO K = 1, 6
         STRESS(K) = 0.D0
         DSTRAN(K) = 0.D0
         PL(K) = 0.D0
      END DO
      DO K = 1, 4
         STATEV(K) = 0.D0
      END DO
      EPS11 = 0.D0
      DL2 = 0.D0
      DL3 = 0.D0
      DO IS = 1, NSTEP
         DO IT = 1, 50
            DO K = 1, 6
               S(K) = STRESS(K)
            END DO
            DO K = 1, 4
               SV(K) = STATEV(K)
            END DO
            DO K = 1, 6
               PLT(K) = PL(K)
            END DO
            DSTRAN(1) = EMAX/DBLE(NSTEP)
            DSTRAN(2) = DL2
            DSTRAN(3) = DL3
            PNEWDT = 1.D0
            CALL CALLU(NTENS, PROPS, S, SV, DSTRAN, D, PNEWDT, PLT)
            R2 = S(2)
            R3 = S(3)
            IF (MAX(ABS(R2),ABS(R3)) .LE. 1.D-9*MAX(1.D0,ABS(S(1))))
     1         GO TO 10
            A = D(2,2)
            B = D(2,3)
            C = D(3,2)
            DD = D(3,3)
            DET = A*DD - B*C
            X2 = ( DD*R2 - B*R3)/DET
            X3 = (-C*R2 + A*R3)/DET
            DL2 = DL2 - X2
            DL3 = DL3 - X3
         END DO
         WRITE(*,*) 'NO CONVERGENCE'
         STOP 1
   10    CONTINUE
         DO K = 1, 6
            STRESS(K) = S(K)
         END DO
         DO K = 1, 4
            STATEV(K) = SV(K)
         END DO
         DO K = 1, 6
            PL(K) = PLT(K)
         END DO
         EPS11 = EPS11 + DSTRAN(1)
         WRITE(*,'(I7,6ES26.17E3,I4,ES12.3,2ES26.17E3)') IS, EPS11,
     1      S(1), SV(1), SV(2), SV(3), SV(4), IT, PNEWDT, PL(1), PL(2)
      END DO
      END
C
      SUBROUTINE MTAN
      IMPLICIT NONE
      INTEGER NTENS, I, J, K
      DOUBLE PRECISION PROPS(7), EQPS0, S0(6), DE(6), S(6), SV(4),
     1 D(6,6), DUM(6,6), SP(6), SM(6), DP(6), H, PNEWDT, PL(6)
      READ(*,*) (PROPS(K), K=1,7)
      READ(*,*) NTENS, EQPS0
      READ(*,*) (S0(K), K=1,NTENS)
      READ(*,*) (DE(K), K=1,NTENS)
      DO K = 1, 6
         S(K) = S0(K)
      END DO
      SV(1) = EQPS0
      SV(2) = 0.D0
      SV(3) = 0.D0
      SV(4) = 0.D0
      DO K = 1, 6
         PL(K) = 0.D0
      END DO
      CALL CALLU(NTENS, PROPS, S, SV, DE, D, PNEWDT, PL)
      WRITE(*,'(4ES26.17E3)') SV(1), SV(2), SV(3), SV(4)
      DO I = 1, NTENS
         WRITE(*,'(6ES26.17E3)') (D(I,J), J=1,NTENS)
      END DO
      H = 1.D-7
      DO J = 1, NTENS
         DO K = 1, 6
            DP(K) = DE(K)
            SP(K) = S0(K)
            SM(K) = S0(K)
         END DO
         DP(J) = DE(J) + H
         SV(1) = EQPS0
         SV(3) = 0.D0
         CALL CALLU(NTENS, PROPS, SP, SV, DP, DUM, PNEWDT, PL)
         DP(J) = DE(J) - H
         SV(1) = EQPS0
         SV(3) = 0.D0
         CALL CALLU(NTENS, PROPS, SM, SV, DP, DUM, PNEWDT, PL)
         WRITE(*,'(6ES26.17E3)') ((SP(I)-SM(I))/(2.D0*H), I=1,NTENS)
      END DO
      END
C
      SUBROUTINE STDB_ABQERR(LOP, STRING, INTV, REALV, CHARV)
      IMPLICIT NONE
      INTEGER LOP, INTV(*)
      DOUBLE PRECISION REALV(*)
      CHARACTER*(*) STRING
      CHARACTER*8 CHARV(*)
      WRITE(*,*) 'ABQERR ', LOP, ' ', TRIM(STRING)
      END
C
      SUBROUTINE XIT
      STOP 2
      END
C
      SUBROUTINE ERHANDLER(FILEIN, MSGID, MSGLVL, LNGSTR, DPERR, CHERR)
      IMPLICIT NONE
      CHARACTER*(*) FILEIN, LNGSTR, CHERR
      INTEGER MSGID, MSGLVL
      DOUBLE PRECISION DPERR(*)
      WRITE(*,*) 'ERHANDLER ', MSGID, MSGLVL, ' ', TRIM(LNGSTR),
     1   ' ', DPERR(1), ' ', TRIM(FILEIN), TRIM(CHERR)
      IF (MSGLVL .GE. 4) STOP 2
      END
