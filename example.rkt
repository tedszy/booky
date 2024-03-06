;;; Tickets for March 28, 2020.

#lang racket

(require "booky.rkt")

(start)

(define t1 (make-ticket #:code "pri"
                        (volume "2016" 35)
                        (volume "2017" 27)
                        (volume "2018" 33)
                        (volume "2019" 28)))

(define t2 (make-ticket #:code "viec"
                        (volume "2016" 33)
                        (volume "2017" 27)
                        (volume "2018" 28)
                        (volume "2019" 27)))

(define t3 (make-ticket #:code "ges"
                        (volume "2016-2017" 31)
                        (volume "2018-2019" 29)))

(define t4 (make-ticket #:code "con"
                        (volume "2016" 38)
                        (volume "2017" 35)
                        (volume "2018" 41)
                        (volume "2019" 28)))

(define t5 (make-ticket #:code "viec"
                        (volume "2016" 33)
                        (volume "2017" 27)
                        (volume "2018" 28)
                        (volume "2019" 27)))

(define t6 (make-ticket #:code "viec"
                        (volume "2016" 33)
                        (volume "2017" 27)
                        (volume "2018" 28)
                        (volume "2019" 27)))

(define t7 (make-ticket #:code "viec"
                        (volume "2016" 33)
                        (volume "2017" 27)
                        (volume "2018" 28)
                        (volume "2019" 27)))

(define t8 (make-ticket #:code "viec"
                        (volume "2016" 33)
                        (volume "2017" 27)
                        (volume "2018" 28)
                        (volume "2019" 27)))

(define t9 (make-ticket #:code "viec"
                        (volume "2016" 33)
                        (volume "2017" 27)
                        (volume "2018" 28)
                        (volume "2019" 27)))

(define t10 (make-ticket #:code "viec"
                        (volume "2016" 33)
                        (volume "2017" 27)
                        (volume "2018" 28)
                        (volume "2019" 27)))

(pdf #:filename "tickets-280320"
     t1 t2 t3 t4 t5 t6 'newpage t7 t8 t9 t10)
