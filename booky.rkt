;;; booky.rkt user interface.
;;;
;;; Documentation -- to do.
;;;


#lang racket

(require "dbms.rkt"
         "tickets.rkt"
         "format-table.rkt")

(provide publication-filename
         upper-margin
         lower-margin
         left-margin
         right-margin
         font-size
         vertical-stretch
         title-width
         title-styling
         label-width
         volume-separation
         ticket-spacing
         
         cardboard-label
         paper-label
         bockram-label 
         backcard-label

         volume
         make-ticket-new 
         make-ticket
         pdflatex-program
         pdf
         start
         find)

(define pdflatex-program (make-parameter "pdflatex"))

(define (make-ticket-new #:title title
                         #:cover-height cover-height
                         #:cover-width cover-width
                         #:color color
                         . volumes)
  (ticket-maker title cover-height cover-width color volumes))

(define (make-ticket #:code code . volumes)
  (match (fetch-ticket-args-by-code code)
    ((vector title cover-height cover-width color)
     (ticket-maker title cover-height cover-width color volumes))
    (_ (error "make-ticket: db code lookup returned no row: " code))))

(define (pdf #:filename filename . tickets )
  (write-to-tex-file (format "~a.tex" filename) tickets)
  (system (format  "pdflatex ~a.tex" filename)))

(define (start)
  (if (conn)
      (begin (drop-publication-table)
             (create-publication-table)
             (populate-publication-table))
      (begin (connect)
             (create-publication-table)
             (populate-publication-table))))

(define (find title-search-string)
  (displayln
   (format-table/simple
    (map (lambda (row)
           (vector->list
            (vector-map (lambda (u)
                          (format "~a" u))
                        row)))
         (fetch-rows-by-title title-search-string)))))
 
